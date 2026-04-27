from flask import Blueprint, request, jsonify
from app import db
from models import Product, User
import jwt
import datetime
import os

products_bp = Blueprint('products', __name__)
health_bp = Blueprint('health', __name__)
auth_bp = Blueprint('auth', __name__)

# --- Health endpoints ---
@health_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.datetime.utcnow().isoformat()})

@health_bp.route('/ready', methods=['GET'])
def readiness_check():
    try:
        db.session.execute(db.text('SELECT 1'))
        return jsonify({'status': 'ready', 'database': 'connected'}), 200
    except Exception as e:
        return jsonify({'status': 'not_ready', 'error': str(e)}), 503

# --- Auth endpoints ---
@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or user.password_hash != password:  # simplified for demo
        return jsonify({'error': 'Invalid credentials'}), 401

    token = jwt.encode(
        {'user_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)},
        os.environ.get('SECRET_KEY', 'dev-secret-key'),
        algorithm='HS256'
    )
    return jsonify({'token': token}), 200

# --- Product endpoints ---
@products_bp.route('/products', methods=['GET'])
def get_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    pagination = Product.query.paginate(page=page, per_page=per_page)
    return jsonify({
        'products': [p.to_dict() for p in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@products_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())

@products_bp.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    required_fields = ['name', 'price']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields: name, price'}), 400

    product = Product(
        name=data['name'],
        description=data.get('description', ''),
        price=data['price'],
        stock=data.get('stock', 0)
    )
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict()), 201

@products_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()

    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.price = data.get('price', product.price)
    product.stock = data.get('stock', product.stock)

    db.session.commit()
    return jsonify(product.to_dict())

@products_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted'}), 200
