from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.services.validators import ConflictError, ValidationError, validate_registration_credentials
from models import User


def authenticate_user(username, password):
    """Verify credentials against the database.

    Returns None on failure — never raises so callers can return a generic
    401 without leaking whether the username exists.
    """
    user = User.query.filter_by(username=username).first()
    if user is None or not check_password_hash(user.password_hash, password):
        return None
    return user


def generate_token(user, expires_in_hours=24):
    payload = {
        'user_id': user.id,
        'role': user.role,
        'exp': datetime.now(timezone.utc) + timedelta(hours=expires_in_hours),
    }
    return jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256',
    )


def register_user(username, password):
    errors = validate_registration_credentials(username, password)
    if errors:
        raise ValidationError(errors[0])

    normalized = str(username).strip()
    existing = User.query.filter_by(username=normalized).first()
    if existing is not None:
        raise ConflictError('Username already taken')

    user = User(
        username=normalized,
        password_hash=generate_password_hash(password),
        role='customer',
    )
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ConflictError('Username already taken') from None

    return user
