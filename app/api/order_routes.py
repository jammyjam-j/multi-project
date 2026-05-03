from flask import Blueprint, jsonify, request

from app.auth import role_required, token_required
from app.extensions import db
from app.services.order_service import (
    create_order,
    list_all_orders,
    list_orders_for_user,
    simulate_payment,
)
from app.services.validators import (
    NotFoundError,
    ServiceError,
    ValidationError,
    validate_order_payload,
)

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('/orders', methods=['POST'])
@token_required
@role_required('customer', 'admin')
def create_order_endpoint(current_user):
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'Order items are required'}), 400

    errors = validate_order_payload(data)
    if errors:
        return jsonify({'error': errors[0]}), 400

    try:
        order = create_order(current_user, data)
    except (NotFoundError, ValidationError) as exc:
        db.session.rollback()
        return jsonify({'error': exc.message}), exc.status_code

    return jsonify(order.to_dict()), 201


@orders_bp.route('/orders/<int:order_id>/simulate-payment', methods=['POST'])
@token_required
@role_required('customer')
def simulate_payment_endpoint(current_user, order_id):
    try:
        order = simulate_payment(current_user, order_id)
    except (NotFoundError, ValidationError, ServiceError) as exc:
        db.session.rollback()
        return jsonify({'error': exc.message}), exc.status_code

    return jsonify(order.to_dict()), 200


@orders_bp.route('/orders/mine', methods=['GET'])
@token_required
@role_required('customer')
def get_my_orders(current_user):
    orders = list_orders_for_user(current_user)
    return jsonify({'orders': [order.to_dict() for order in orders]}), 200


@orders_bp.route('/orders', methods=['GET'])
@token_required
@role_required('admin')
def get_all_orders(current_user):
    # FIXME: this returns ALL orders without pagination — will break with large datasets
    orders = list_all_orders()
    return jsonify({'orders': [order.to_dict() for order in orders]}), 200
