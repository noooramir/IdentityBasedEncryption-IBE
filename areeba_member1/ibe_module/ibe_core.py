from __future__ import annotations


def setup():
    """Placeholder for Boneh-Franklin KGC setup."""
    # Only public parameters are returned here; the master secret stays
    # internal to the KGC boundary and is never exposed by the API.
    return {
        "success": True,
        "public_params": {
            "curve": "SS512",
            "generator": "dummy_generator",
            "hash_function": "SHA-256",
        },
        "message": "Boneh-Franklin public parameters mock generated.",
    }


def extract(identity: str):
    """Placeholder for identity key extraction."""
    return {
        "success": True,
        "identity": identity,
        "private_key": f"mock-private-key-for:{identity}",
        "message": "Mock private key generated.",
    }


def encrypt(public_params, identity: str, message: str):
    """Placeholder for identity-based encryption."""
    return {
        "success": True,
        "public_params": public_params,
        "identity": identity,
        "ciphertext": f"mock-ciphertext-for:{identity}",
        "message_preview": message,
        "message": "Mock encryption completed.",
    }


def decrypt(ciphertext, private_key):
    """Placeholder for identity-based decryption."""
    return {
        "success": True,
        "ciphertext": ciphertext,
        "private_key": private_key,
        "plaintext": "mock-plaintext",
        "message": "Mock decryption completed.",
    }


def setup_ibe_system():
    """Backward-compatible alias for older callers."""
    return setup()


def extract_private_key(identity: str):
    """Backward-compatible alias for older callers."""
    return extract(identity)


def encrypt_for_identity(identity: str, message: str):
    """Backward-compatible alias for older callers."""
    return encrypt(setup()["public_params"], identity, message)


def decrypt_for_identity(identity: str, ciphertext):
    """Backward-compatible alias for older callers."""
    return decrypt(ciphertext, f"mock-private-key-for:{identity}")
