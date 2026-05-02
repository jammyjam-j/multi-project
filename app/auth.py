from functools import wraps

import jwt
from flask import current_app, jsonify, request

from app.extensions import db
from models import User

ROLE_ALIASES = {
    'customer': {'customer', 'user'},
    'user': {'user', 'customer'},
}


def token_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        header = request.headers.get('Authorization', '')
        token = header.replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256'],
            )
            current_user = db.session.get(User, payload['user_id'])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except Exception:
            return jsonify({'error': 'Invalid token'}), 401

        if current_user is None:
            return jsonify({'error': 'Invalid token'}), 401

        return view(current_user=current_user, *args, **kwargs)

    return wrapped


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(current_user=None, *args, **kwargs):
            allowed_roles = set(roles)
            for role in roles:
                allowed_roles.update(ROLE_ALIASES.get(role, set()))

            if current_user is None or current_user.role not in allowed_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return view(current_user=current_user, *args, **kwargs)

        return wrapped

    return decorator
