# app/core/onboarding_velocity.py
"""
Tracks onboarding attempts per device fingerprint — same sliding-window
pattern as Project 1's velocity_engine. In-memory for portfolio scale;
Redis in production (see Project 1's scaling roadmap).
"""
import threading
from collections import defaultdict
from datetime import datetime, timedelta, timezone

_lock = threading.Lock()
_device_history: dict[str, list] = defaultdict(list)


def record_attempt(device_fingerprint: str, record_id: str) -> None:
    with _lock:
        now = datetime.now(timezone.utc)
        _device_history[device_fingerprint].append((now, record_id))
        cutoff = now - timedelta(hours=24)
        _device_history[device_fingerprint] = [
            (ts, rid) for ts, rid in _device_history[device_fingerprint] if ts > cutoff
        ]


def get_velocity_features(device_fingerprint: str) -> dict:
    with _lock:
        history = _device_history.get(device_fingerprint, [])
        unique_records = {rid for _, rid in history}
        return {
            "onboarding_attempts_24h": len(history),
            "device_fingerprint_reuse": max(0, len(unique_records) - 1),
        }