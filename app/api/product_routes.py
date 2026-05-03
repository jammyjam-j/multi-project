from flask import Blueprint, jsonify, request

from app.auth import role_required, token_required
from app.services.cache_service import cache_get, cache_invalidate, cache_set
from app.services.catalog_service import (
    create_category as create_category_record,
    create_product as create_product_record,
    delete_category as delete_category_record,
    delete_product as delete_product_record,
    update_category as update_category_record,
    update_product as update_product_record,
)
from app.services.validators import (
    ConflictError,
    validate_category_name,
    validate_category_payload,
    validate_product_payload,
)
from models import Category, Product

products_bp = Blueprint('products', __name__)
categories_bp = Blueprint('categories', __name__)


@products_bp.route('/products', methods=['GET'])
def get_products():
    # TODO: add category filter and search params here
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    cache_key = f'products:{page}:{per_page}'
    cached = cache_get(cache_key)
    if cached is not None:
        return jsonify(cached)

    pagination = Product.query.paginate(page=page, per_page=per_page)
    result = {
        'products': [product.to_dict() for product in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
    }
    cache_set(cache_key, result, ttl=30)
    return jsonify(result)


@products_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())


@products_bp.route('/products', methods=['POST'])
@token_required
@role_required('admin')
def create_product(current_user):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be valid JSON'}), 400

    errors = validate_product_payload(data, require_name=True, require_price=True)
    if errors:
        return jsonify({'error': errors[0]}), 400

    product = create_product_record(data)
    return jsonify(product.to_dict()), 201


@products_bp.route('/products/<int:product_id>', methods=['PUT'])
@token_required
@role_required('admin')
def update_product(current_user, product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be valid JSON'}), 400

    errors = validate_product_payload(data, require_name=False, require_price=False)
    if errors:
        return jsonify({'error': errors[0]}), 400

    product = update_product_record(product, data)
    return jsonify(product.to_dict())


@products_bp.route('/products/<int:product_id>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_product(current_user, product_id):
    product = Product.query.get_or_404(product_id)
    delete_product_record(product)
    return jsonify({'message': 'Product removed from catalog'}), 200


@categories_bp.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([category.to_dict() for category in categories])


@categories_bp.route('/categories', methods=['POST'])
@token_required
@role_required('admin')
def create_category(current_user):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be valid JSON'}), 400

    errors = validate_category_payload(data, require_name=True)
    if errors:
        return jsonify({'error': errors[0]}), 400

    try:
        category = create_category_record(data)
    except ConflictError as exc:
        return jsonify({'error': exc.message}), exc.status_code
    return jsonify(category.to_dict()), 201


@categories_bp.route('/categories/<int:category_id>', methods=['PUT'])
@token_required
@role_required('admin')
def update_category(current_user, category_id):
    category = Category.query.get_or_404(category_id)
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body must be valid JSON'}), 400

    if 'name' in data:
        new_name = validate_category_name(data['name'])
        if not new_name:
            return jsonify({'error': 'Category name cannot be blank'}), 400

    try:
        category = update_category_record(category, data)
    except ConflictError as exc:
        return jsonify({'error': exc.message}), exc.status_code
    return jsonify(category.to_dict())


@categories_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_category(current_user, category_id):
    category = Category.query.get_or_404(category_id)
    delete_category_record(category)
    return jsonify({'message': 'Category removed'}), 200
