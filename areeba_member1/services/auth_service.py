from __future__ import annotations

from database import create_user, get_user_public
from api_response import error_response, success_response
from request_security import validate_json_payload


def register_user(payload):
    # Keep the route layer thin: validation and persistence live outside the blueprint.
    payload, error_message = validate_json_payload(payload, ("identity",))
    if error_message is not None:
        return error_response(error_message)

    identity = payload["identity"].strip()
    if get_user_public(identity) is not None:
        return error_response("identity already registered.", 409)

    try:
        user = create_user(identity)
    except ValueError:
        return error_response("identity already registered.", 409)

    return success_response(
        {"id": user.id, "identity": user.identity},
        message="Identity registered successfully.",
        status_code=201,
    )