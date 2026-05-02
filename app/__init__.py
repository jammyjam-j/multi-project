import json
import logging
import sys
import time
from flask import Flask, jsonify, has_request_context, render_template, request
from flask_cors import CORS
from datetime import datetime
from app.extensions import db


def setup_structured_logging(app):
    handler_name = 'structured_stdout'

    class JsonFormatter(logging.Formatter):
        def format(self, record):
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': record.levelname,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName,
            }
            if has_request_context():
                log_entry['request'] = {
                    'method': request.method,
                    'path': request.path,
                    'remote_addr': request.remote_addr,
                }
            return json.dumps(log_entry)

    structured_handler = None
    for handler in app.logger.handlers:
        if getattr(handler, 'name', '') == handler_name:
            structured_handler = handler
            break

    if structured_handler is None:
        structured_handler = logging.StreamHandler(sys.stdout)
        structured_handler.name = handler_name
        app.logger.addHandler(structured_handler)

    structured_handler.setFormatter(JsonFormatter())
    app.logger.setLevel(logging.INFO)


def create_app(config=None):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    CORS(app)

    if config is None:
        from config import Config
        app.config.from_object(Config)
    else:
        app.config.from_mapping(config)

    setup_structured_logging(app)

    db.init_app(app)

    @app.before_request
    def log_request():
        request.start_time = time.time()

    @app.after_request
    def log_response(response):
        duration = time.time() - getattr(request, 'start_time', time.time())
        app.logger.info(
            f'{request.method} {request.path} {response.status_code} {duration*1000:.1f}ms'
        )
        return response

    @app.route('/')
    def index():
        return render_template('index.html')

    from app.api import auth_bp, categories_bp, health_bp, orders_bp, products_bp

    app.register_blueprint(products_bp, url_prefix='/api/v1')
    app.register_blueprint(health_bp, url_prefix='/api/v1')
    app.register_blueprint(auth_bp, url_prefix='/api/v1')
    app.register_blueprint(categories_bp, url_prefix='/api/v1')
    app.register_blueprint(orders_bp, url_prefix='/api/v1')

    from app.api.health_routes import health_check, readiness_check

    app.add_url_rule('/health', 'liveness_root', health_check)
    app.add_url_rule('/ready', 'readiness_root', readiness_check)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

    return app
