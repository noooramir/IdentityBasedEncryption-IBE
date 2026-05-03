from __future__ import annotations

from datetime import datetime, timezone


MAX_REQUEST_SKEW_SECONDS = 300


def validate_request_timestamp(raw_timestamp: str | None) -> str | None:
    """Reject stale or future-dated requests to reduce replay risk.

    The API expects clients to send a Unix timestamp in the
    X-Request-Timestamp header. We keep the check simple: only a small
    clock skew window is accepted, and the timestamp is never logged.
    """

    if raw_timestamp is None:
        return "X-Request-Timestamp header is required."

    try:
        request_timestamp = int(raw_timestamp)
    except (TypeError, ValueError):
        return "X-Request-Timestamp must be a Unix timestamp."

    current_timestamp = int(datetime.now(timezone.utc).timestamp())
    if abs(current_timestamp - request_timestamp) > MAX_REQUEST_SKEW_SECONDS:
        return "Request timestamp is outside the allowed time window."

    return None

def validate_json_payload(payload, required_fields: tuple[str, ...]) -> tuple[dict | None, str | None]:
    """Validate that a decoded JSON body exists and contains required fields."""
    if not isinstance(payload, dict):
        return None, "Request body must be valid JSON."
    for field in required_fields:
        value = payload.get(field)
        if value is None:
            return None, f"{field} is required."
        if isinstance(value, str) and not value.strip():
            return None, f"{field} is required."
    return payload, None