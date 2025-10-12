from flask import Blueprint, Response, jsonify, request
from pydantic import ValidationError

from backend.webapp.auth.domain.dtos import UserLoginInputDTO
from backend.webapp.auth.domain.enums import LoginStatus, RegistrationStatus
from backend.webapp.auth.domain.service.jwt import JwtService
from backend.webapp.auth.domain.service.login import LoginService
from backend.webapp.auth.domain.service.register import RegistrationService
from backend.webapp.auth.infrastructure.repository import (
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
    data = request.get_json()
    result = RegistrationService(UsersDatabaseRepository(db.session)).register(
        data["email"], data["password"]
    )
    if result.status == RegistrationStatus.failure:
        return jsonify({"error": result.reason}), 400
    return jsonify({"message": "success"}), 201
