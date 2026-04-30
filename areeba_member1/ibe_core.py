"""
# file name : ibe_core.py
Boneh-Franklin style IBE (teaching prototype) built with Charm-Crypto.

This module covers Member 1 responsibilities:
- Master setup at KGC
- Private key extraction for identity
- IBE encrypt/decrypt by identity

Note:
- This is for academic/demo use.
- In production, add authenticated channels, strict validation, and key storage hardening.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from charm.core.math.pairing import hashPair
from charm.toolbox.pairinggroup import GT, PairingGroup
from charm.toolbox.symcrypto import SymmetricCryptoAbstraction
from charm.schemes.ibenc.ibenc_bf01 import IBE_BonehFranklin


@dataclass
class KGCState:
    """Holds KGC cryptographic state."""

    group_obj: PairingGroup
    ibe_scheme: IBE_BonehFranklin
    master_public_key: Dict[str, Any]
    master_secret_key: Dict[str, Any]


def kgc_setup(pairing_curve: str = "SS512") -> KGCState:
    """
    Initialize pairing group and generate master keys.

    Args:
        pairing_curve: Pairing curve identifier from Charm-Crypto.

    Returns:
        KGCState containing scheme, MPK, and MSK.
    """
    group = PairingGroup(pairing_curve)
    ibe = IBE_BonehFranklin(group)
    mpk, msk = ibe.setup()
    return KGCState(group_obj=group, ibe_scheme=ibe, master_public_key=mpk, master_secret_key=msk)


def extract_private_key(kgc: KGCState, identity: str) -> Dict[str, Any]:
    """
    Generate user private key for a specific identity.

    Args:
        kgc: KGC state with master secret.
        identity: User identity string (e.g., email).
    """
    if not identity or not identity.strip():
        raise ValueError("identity must be a non-empty string")
    return kgc.ibe_scheme.extract(kgc.master_secret_key, identity.strip())


def encrypt_for_identity(kgc: KGCState, identity: str, message: str) -> Dict[str, Any]:
    """
    Encrypt a message under recipient identity.

    Args:
        kgc: KGC state containing public params.
        identity: Recipient identity.
        message: Plaintext message.
    """
    if not message:
        raise ValueError("message must be non-empty")
    session_element = kgc.group_obj.random(GT)
    ciphertext = kgc.ibe_scheme.encrypt(kgc.master_public_key, identity.strip(), session_element)
    symmetric_key = hashPair(session_element)
    sym = SymmetricCryptoAbstraction(symmetric_key)
    encrypted_message = sym.encrypt(message)
    return {
        "identity": identity.strip(),
        "ciphertext": ciphertext,
        "session_element": session_element,
        "encrypted_message": encrypted_message,
    }


def decrypt_for_identity(
    kgc: KGCState,
    user_private_key: Dict[str, Any],
    encrypted_bundle: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Decrypt and verify recovered session element.

    Uses recovered GT element to derive a symmetric key and decrypt payload.
    """
    recovered_element = kgc.ibe_scheme.decrypt(
        kgc.master_public_key,
        user_private_key,
        encrypted_bundle["ciphertext"],
    )
    recovered_key = hashPair(recovered_element)
    sym = SymmetricCryptoAbstraction(recovered_key)
    recovered_message = sym.decrypt(encrypted_bundle["encrypted_message"])
    return {
        "ibe_session_valid": recovered_element == encrypted_bundle["session_element"],
        "message": recovered_message.decode("utf-8"),
    }


def demo_run() -> None:
    """Minimal local demo for quick validation."""
    print("[1] KGC setup")
    kgc = kgc_setup()

    recipient_id = "noor@group.edu"
    print(f"[2] Extract private key for identity: {recipient_id}")
    sk_id = extract_private_key(kgc, recipient_id)

    print("[3] Encrypt for recipient identity")
    bundle = encrypt_for_identity(kgc, recipient_id, "Confidential draft")

    print("[4] Decrypt and validate")
    result = decrypt_for_identity(kgc, sk_id, bundle)
    print("IBE session validation:", "SUCCESS" if result["ibe_session_valid"] else "FAILED")
    print("Recovered message:", result["message"])


if __name__ == "__main__":
    demo_run()
