from __future__ import annotations

from flask import Blueprint, request

from services.ibe_service import (
    decrypt_message as decrypt_message_service,
    encrypt_message as encrypt_message_service,
    extract_private_key as extract_private_key_service,
    get_ibe_status,
    get_public_params,
)


ibe_bp = Blueprint("ibe", __name__)


@ibe_bp.get("/ibe/status")
def ibe_status():
    return get_ibe_status()


@ibe_bp.get("/public-params")
def public_params():
    return get_public_params()


@ibe_bp.post("/extract-key")
def extract_key():
    return extract_private_key_service(request.get_json(silent=True))


@ibe_bp.post("/encrypt")
def encrypt_message_route():
    return encrypt_message_service(request.get_json(silent=True))


@ibe_bp.post("/decrypt")
def decrypt_message_route():
    return decrypt_message_service(request.get_json(silent=True))
