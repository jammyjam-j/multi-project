from flask import Blueprint, current_app, jsonify, request

from app.services.auth_service import authenticate_user, generate_token, register_user
from app.services.validators import ConflictError, ValidationError

auth_bp = Blueprint('auth', __name__)


def _get_limiter():
    """Get the limiter from the app."""
    return getattr(current_app, 'limiter', None)


@auth_bp.route('/auth/register', methods=['POST'])
def register():
    limiter = _get_limiter()
    if limiter:
        limiter.limit("5 per minute")

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Registration requires a JSON body with username and password'}), 400

    username = data.get('username')
    password = data.get('password')
    try:
        user = register_user(username, password)
    except ValidationError as exc:
        return jsonify({'error': exc.message}), exc.status_code
    except ConflictError as exc:
        return jsonify({'error': exc.message}), exc.status_code

    token = generate_token(user)
    return jsonify({'token': token}), 201


@auth_bp.route('/auth/login', methods=['POST'])
def login():
    limiter = _get_limiter()
    if limiter:
        limiter.limit("10 per minute")

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Login requires a JSON body with username and password'}), 400

    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Both username and password are required'}), 400

    user = authenticate_user(username, password)
    if user is None:
        return jsonify({'error': 'Invalid credentials'}), 401

    token = generate_token(user)
    return jsonify({'token': token}), 200
