from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

def create_app(config=None):
    app = Flask(__name__)
    CORS(app)

    # Configuration
    if config is None:
        from config import Config
        app.config.from_object(Config)
    else:
        app.config.from_mapping(config)

    # Extensions
    db.init_app(app)

    # Register blueprints
    from routes import products_bp, health_bp, auth_bp
    app.register_blueprint(products_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

    # Create tables
    with app.app_context():
        db.create_all()

    return app
