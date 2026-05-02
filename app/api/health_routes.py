import datetime

from flask import Blueprint, jsonify

from app.extensions import db

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.datetime.utcnow().isoformat()})


@health_bp.route('/ready', methods=['GET'])
def readiness_check():
    try:
        db.session.execute(db.text('SELECT 1'))
        return jsonify({'status': 'ready', 'database': 'connected'}), 200
    except Exception:
        return jsonify({'status': 'not_ready', 'reason': 'database unavailable'}), 503
