# app/streaming/consumer.py
"""
Consumer thread — same architecture as Project 1: daemon thread,
thread-safe results store, Kafka-availability check with backoff
(handles Render's no-Kafka environment gracefully).
"""
import json
import logging
import threading
from datetime import datetime, timezone

from confluent_kafka import Consumer, KafkaError, Producer

from app.config import (
    KAFKA_BOOTSTRAP_SERVERS, KAFKA_CONSUMER_GROUP,
    KAFKA_KYC_EVENTS_TOPIC, KAFKA_KYC_RESULTS_TOPIC,
)

logger = logging.getLogger(__name__)
_kafka_logger = logging.getLogger("confluent_kafka")
_kafka_logger.setLevel(logging.ERROR)

_results_store: dict[str, dict] = {}
_lock = threading.Lock()
_stats = {"consumed": 0, "flagged": 0}
_stop_event = threading.Event()
_thread = None


def store_result(record_id: str, assessment: dict) -> None:
    with _lock:
        _results_store[record_id] = assessment
        if len(_results_store) > 1000:
            del _results_store[next(iter(_results_store))]


def get_result(record_id: str):
    with _lock:
        return _results_store.get(record_id)


def get_all_results() -> list[dict]:
    with _lock:
        return sorted(_results_store.values(), key=lambda x: x.get("scored_at", ""), reverse=True)


def get_consumer_stats() -> dict:
    return {**_stats, "results_in_store": len(_results_store),
            "running": _thread is not None and _thread.is_alive()}


def _kafka_available(timeout=2.0) -> bool:
    from confluent_kafka.admin import AdminClient
    try:
        AdminClient({"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS}).list_topics(timeout=timeout)
        return True
    except Exception:
        return False


def _run():
    consumer = Consumer({
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "group.id": KAFKA_CONSUMER_GROUP,
        "auto.offset.reset": "earliest",
        "logger": _kafka_logger,
    })
    results_producer = Producer({"bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS, "logger": _kafka_logger})

    connected, warned = False, False
    try:
        while not _stop_event.is_set():
            if not connected:
                if _kafka_available():
                    consumer.subscribe([KAFKA_KYC_EVENTS_TOPIC])
                    connected = True
                    logger.info("✅ KYC consumer subscribed")
                else:
                    if not warned:
                        logger.warning("⚠️ Kafka unreachable — retrying every 60s")
                        warned = True
                    if _stop_event.wait(60):
                        break
                    continue

            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    logger.error(f"Consumer error: {msg.error()}")
                continue

            try:
                raw = json.loads(msg.value().decode())
                assessment = raw.get("data", raw)
                record_id = assessment["record_id"]
                store_result(record_id, assessment)

                results_producer.produce(
                    topic=KAFKA_KYC_RESULTS_TOPIC,
                    key=record_id.encode(),
                    value=json.dumps(assessment, default=str).encode(),
                )
                results_producer.poll(0)

                _stats["consumed"] += 1
                if assessment.get("decision") != "APPROVE":
                    _stats["flagged"] += 1
            except Exception as e:
                logger.error(f"Processing error: {e}")
    finally:
        consumer.close()
        results_producer.flush(timeout=5)


def start_consumer() -> bool:
    global _thread
    _stop_event.clear()
    _thread = threading.Thread(target=_run, name="kyc-consumer", daemon=True)
    _thread.start()
    return True


def stop_consumer() -> None:
    _stop_event.set()
    if _thread:
        _thread.join(timeout=10)