"""Authentication routes for NEXORA AI."""

from uuid import UUID

from quart import Blueprint, jsonify, request

from auth.jwt_utils import create_access_token, create_refresh_token, decode_token, get_user_id_from_token
from db import AsyncSessionLocal
from models.token import RefreshToken
from schemas import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse, RefreshTokenRequest
from services.user_service import UserService

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
async def register():
    """Register a new user."""
    try:
        data = await request.get_json()
        req = UserRegisterRequest(**data)

        async with AsyncSessionLocal() as session:
            user = await UserService.create_user(
                session,
                email=req.email,
                password=req.password,
                full_name=req.full_name or "",
            )

            access_token = create_access_token(user.id, user.email)
            refresh_token = create_refresh_token(user.id)

            # Store refresh token
            refresh_token_obj = RefreshToken(
                user_id=user.id,
                token_hash=refresh_token,
                expires_at=refresh_token,  # In production, calculate proper expiry
            )
            session.add(refresh_token_obj)
            await session.commit()

            return jsonify(
                {
                    "user": UserResponse.model_validate(user).model_dump(),
                    "token": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "token_type": "bearer",
                        "expires_in": 1800,
                    },
                }
            ), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Registration failed"}), 500


@auth_bp.route("/login", methods=["POST"])
async def login():
    """Login user."""
    try:
        data = await request.get_json()
        req = UserLoginRequest(**data)

        async with AsyncSessionLocal() as session:
            user = await UserService.authenticate_user(session, req.email, req.password)
            if not user:
                return jsonify({"error": "Invalid email or password"}), 401

            access_token = create_access_token(user.id, user.email)
            refresh_token = create_refresh_token(user.id)

            # Store refresh token
            refresh_token_obj = RefreshToken(
                user_id=user.id,
                token_hash=refresh_token,
                expires_at=refresh_token,
            )
            session.add(refresh_token_obj)
            await session.commit()

            return jsonify(
                {
                    "user": UserResponse.model_validate(user).model_dump(),
                    "token": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "token_type": "bearer",
                        "expires_in": 1800,
                    },
                }
            ), 200
    except Exception as e:
        return jsonify({"error": "Login failed"}), 500


@auth_bp.route("/refresh", methods=["POST"])
async def refresh():
    """Refresh access token."""
    try:
        data = await request.get_json()
        req = RefreshTokenRequest(**data)

        # Decode refresh token
        user_id = get_user_id_from_token(req.refresh_token)

        async with AsyncSessionLocal() as session:
            user = await UserService.get_user_by_id(session, user_id)
            if not user:
                return jsonify({"error": "User not found"}), 401

            access_token = create_access_token(user.id, user.email)

            return jsonify(
                {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "expires_in": 1800,
                }
            ), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": "Token refresh failed"}), 500


@auth_bp.route("/me", methods=["GET"])
async def get_current_user():
    """Get current user info (requires valid token)."""
    try:
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid authorization header"}), 401

        token = auth_header.split(" ")[1]
        user_id = get_user_id_from_token(token)

        async with AsyncSessionLocal() as session:
            user = await UserService.get_user_by_id(session, user_id)
            if not user:
                return jsonify({"error": "User not found"}), 404

            return jsonify(UserResponse.model_validate(user).model_dump()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": "Failed to get user info"}), 500
