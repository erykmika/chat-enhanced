from typing import Any

from flask import Blueprint, Response, jsonify, request
from pydantic import ValidationError

from backend.common.jwt import JwtService
from backend.webapp.auth.domain.dtos import (
    UserConfirmationInput,
    UserLoginInputDTO,
)
from backend.webapp.auth.domain.enums import LoginStatus, RegistrationStatus
from backend.webapp.auth.domain.service.confirm import UserConfirmationService
from backend.webapp.auth.domain.service.login import LoginService
from backend.webapp.auth.domain.service.register import RegistrationService
from backend.webapp.auth.infrastructure.external import (
    UserConfirmationMailDelivery,
)
from backend.webapp.auth.infrastructure.repository import (
    ConfirmationDatabaseRepository,
    UsersDatabaseRepository,
)
from backend.webapp.config import JWT_SECRET
from backend.webapp.database import db

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def get_jwt_service() -> JwtService:
    assert JWT_SECRET
    return JwtService(JWT_SECRET)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    try:
        login_dto = UserLoginInputDTO(**data)
    except ValidationError:
        return Response(status=400)

    result = LoginService(UsersDatabaseRepository(db.session)).login(login_dto)
    if result.status != LoginStatus.successful:
        return jsonify({"error": "Unauthorized"}), 401

    token = get_jwt_service().encode(
        {"email": result.user.email, "role": result.user.role}
    )
    return jsonify({"access_token": token})


@auth_bp.route("/register", methods=["POST"])
def register():
    data: dict[str, Any] = request.get_json()  # type: ignore

    try:
        email, password = data["email"], data["password"]
    except KeyError:
        return jsonify({"error": "invalid credentials"}), 400

    result = RegistrationService(
        UsersDatabaseRepository(db.session),
        UserConfirmationMailDelivery(),
        ConfirmationDatabaseRepository(db.session),
    ).register(email, password)

    if result.status == RegistrationStatus.failure:
        return jsonify({"error": result.reason}), 400
    else:
        return jsonify({"message": "success, confirmation link sent"}), 201


@auth_bp.route("/confirm", methods=["POST"])
def confirm():
    """Confirm user creation using a token"""
    data: dict[str, Any] = request.get_json()  # type: ignore

    try:
        email, token = data["email"], data["token"]
    except KeyError:
        return jsonify({"error": "invalid data"}), 400

    result = UserConfirmationService(
        delivery_service=UserConfirmationMailDelivery(),
        repository=ConfirmationDatabaseRepository(db.session),
    ).confirm(input_dto=UserConfirmationInput(email=email, token=token))

    if result.success:
        return jsonify({"message": "success"}), 200
    else:
        return jsonify({"message": "failure", "reason": result.reason}), 400
