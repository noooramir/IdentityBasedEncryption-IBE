from __future__ import annotations
import json
from flask import current_app
from api_response import error_response, success_response
from database import get_user_public, save_private_key
from ibe_module.ibe_core import decrypt, encrypt, extract, setup
from request_security import validate_json_payload

def get_ibe_status():
    return success_response({"message": "IBE module scaffold is ready."})

def get_public_params():
    setup_result = setup()
    return success_response(setup_result["public_params"])

def extract_private_key(payload):
    payload, error_message = validate_json_payload(payload, ("identity",))
    if error_message is not None:
        return error_response(error_message)
    identity = payload["identity"].strip()
    if get_user_public(identity) is None:
        return error_response("identity is not registered.", 404)
    current_app.logger.info("Key generation requested for identity=%s", identity)
    result = extract(identity)
    save_private_key(identity, result["private_key"])
    return success_response({"identity": result["identity"], "private_key": result["private_key"]})

def encrypt_message(payload):
    payload, error_message = validate_json_payload(payload, ("receiver_id", "message"))
    if error_message is not None:
        return error_response(error_message)
    receiver_id = payload["receiver_id"].strip()
    message = payload["message"].strip()
    if get_user_public(receiver_id) is None:
        return error_response("receiver_id is not registered.", 404)
    current_app.logger.info("Encryption requested for receiver_id=%s", receiver_id)
    public_params = setup()["public_params"]
    result = encrypt(public_params, receiver_id, message)
    return success_response(
        {
            "receiver_id": receiver_id,
            "ciphertext": result["ciphertext"],
        }
    )

def decrypt_message(payload):
    current_app.logger.info("Decrypt payload received: %s", payload)
    payload, error_message = validate_json_payload(payload, ("ciphertext", "private_key"))
    if error_message is not None:
        return error_response(error_message)
    ciphertext = payload["ciphertext"]
    private_key = payload["private_key"]
    if isinstance(ciphertext, dict):
        ciphertext = json.dumps(ciphertext)
    else:
        ciphertext = ciphertext.strip()
    private_key = private_key.strip()
    current_app.logger.info("Decryption requested")
    result = decrypt(ciphertext, private_key)
    if not result["success"]:
        return error_response(result.get("error", "Decryption failed."), 400)
    return success_response({"plaintext": result["plaintext"]})