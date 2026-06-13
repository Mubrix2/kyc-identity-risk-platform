# app/streaming/producer.py
"""Kafka producer for kyc-events — same singleton pattern as Project 1."""
import json
import logging
from datetime import datetime, timezone

from confluent_kafka import Producer

from app.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_KYC_EVENTS_TOPIC

logger = logging.getLogger(__name__)
_kafka_logger = logging.getLogger("confluent_kafka")
_kafka_logger.setLevel(logging.ERROR)

_producer = None


def initialise_producer() -> bool:
    global _producer
    try:
        _producer = Producer({
            "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
            "acks": "all",
            "linger.ms": 5,
            "logger": _kafka_logger,
        })
        logger.info(f"Kafka producer ready | {KAFKA_BOOTSTRAP_SERVERS}")
        return True
    except Exception as e:
        logger.error(f"Producer init failed: {e}")
        return False


def publish_assessment(assessment: dict) -> bool:
    if _producer is None:
        return False
    try:
        _producer.produce(
            topic=KAFKA_KYC_EVENTS_TOPIC,
            key=assessment["record_id"].encode(),
            value=json.dumps({
                "data": assessment,
                "published_at": datetime.now(timezone.utc).isoformat(),
            }, default=str).encode(),
        )
        _producer.poll(0)
        return True
    except Exception as e:
        logger.error(f"Publish failed: {e}")
        return False


def shutdown_producer() -> None:
    if _producer:
        _producer.flush(timeout=10)