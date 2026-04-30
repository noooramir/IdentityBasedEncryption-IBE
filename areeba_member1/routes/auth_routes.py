from __future__ import annotations

from flask import Blueprint, request 

from services.auth_service import register_user


auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register_identity():
    return register_user(request.get_json(silent=True))
