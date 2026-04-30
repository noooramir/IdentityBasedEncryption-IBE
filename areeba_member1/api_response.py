from __future__ import annotations

from flask import jsonify


def success_response(data=None, message: str | None = None, status_code: int = 200):
    payload = {"status": "success", "data": data}
    if message is not None:
        payload["message"] = message
    return jsonify(payload), status_code


def error_response(message: str, status_code: int = 400):
    return jsonify({"status": "error", "message": message}), status_code