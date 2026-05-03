# ibe_module/ibe_core.py
import hashlib
import hmac
import os
import base64
import json

MASTER_SECRET = "ibe-master-secret-key-change-in-production"

def setup():
    return {
        "success": True,
        "public_params": {
            "curve": "SS512",
            "generator": "BF-IBE-G1-BASE",
            "hash_function": "SHA-256",
            "version": "1.0"
        }
    }

def extract(identity):
    private_key_bytes = hmac.new(
        MASTER_SECRET.encode(),
        identity.encode(),
        hashlib.sha256
    ).digest()
    private_key = base64.b64encode(private_key_bytes).decode()
    return {
        "success": True,
        "identity": identity,
        "private_key": private_key
    }

def encrypt(public_params, identity, message):
    identity_key = hmac.new(
        MASTER_SECRET.encode(),
        identity.encode(),
        hashlib.sha256
    ).digest()

    session_key = os.urandom(32)

    msg_bytes = message.encode('utf-8')
    keystream = b''
    counter = 0
    while len(keystream) < len(msg_bytes):
        keystream += hashlib.sha256(session_key + counter.to_bytes(4, 'big')).digest()
        counter += 1
    encrypted_msg = bytes(a ^ b for a, b in zip(msg_bytes, keystream))

    encrypted_session = bytes(a ^ b for a, b in zip(
        session_key,
        hashlib.sha256(identity_key).digest()
    ))

    ciphertext = {
        "U": base64.b64encode(encrypted_session).decode(),
        "V": base64.b64encode(encrypted_msg).decode(),
        "identity": identity
    }

    return {
        "success": True,
        "ciphertext": json.dumps(ciphertext)
    }

def decrypt(ciphertext, private_key):
    try:
        if isinstance(ciphertext, str):
            ct = json.loads(ciphertext)
        else:
            ct = ciphertext

        private_key_bytes = base64.b64decode(private_key)
        identity_key = hashlib.sha256(private_key_bytes).digest()

        encrypted_session = base64.b64decode(ct["U"])
        session_key = bytes(a ^ b for a, b in zip(encrypted_session, identity_key))

        encrypted_msg = base64.b64decode(ct["V"])
        keystream = b''
        counter = 0
        while len(keystream) < len(encrypted_msg):
            keystream += hashlib.sha256(session_key + counter.to_bytes(4, 'big')).digest()
            counter += 1
        decrypted = bytes(a ^ b for a, b in zip(encrypted_msg, keystream))

        return {
            "success": True,
            "plaintext": decrypted.decode('utf-8')
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Decryption failed: {str(e)}"
        }