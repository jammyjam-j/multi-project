import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///products.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_EXPIRATION_HOURS = 24
    API_TIMEOUT_SECONDS = int(os.environ.get('API_TIMEOUT', '30'))

    # Fail fast if dev secret is used outside of development/testing
    if SECRET_KEY == 'dev-secret-key-change-in-production':
        if not os.environ.get('FLASK_DEBUG') and os.environ.get('ENV') != 'development':
            raise RuntimeError(
                'SECRET_KEY must be set for production use. '
                'Set the SECRET_KEY environment variable.'
            )
