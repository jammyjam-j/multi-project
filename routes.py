from flask import Blueprint, request, jsonify, current_app
from functools import wraps
from app import db
from models import Product, User
from werkzeug.security import check_password_hash
import jwt
import datetime

products_bp = Blueprint('products', __name__)
health_bp = Blueprint('health', __name__)
auth_bp = Blueprint('auth', __name__)

# --- JWT decorator with role enforcement ---
def token_required(f):
    """Require a valid JWT; pass current_user to the endpoint."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        try:
            data = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            current_user = db.session.get(User, data['user_id'])
            if not current_user:
                return jsonify({'error': 'Invalid token'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except Exception:
            return jsonify({'error': 'Invalid token'}), 401
        return f(current_user=current_user, *args, **kwargs)
    return decorated

def role_required(*roles):
    """Enforce role-based access control."""
    def decorator(f):
        @wraps(f)
        def decorated(current_user=None, *args, **kwargs):
            if current_user.role not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(current_user=current_user, *args, **kwargs)
        return decorated
    return decorator

# --- Health endpoints ---
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

# --- Auth endpoints ---
@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = jwt.encode(
        {'user_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)},
        current_app.config['SECRET_KEY'],
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
@token_required
@role_required('user', 'admin')
def create_product(current_user):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    required_fields = ['name', 'price']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields: name, price'}), 400

    # Stronger validation
    if not data['name'] or len(str(data['name']).strip()) < 1:
        return jsonify({'error': 'Name cannot be empty'}), 400
    if data['price'] is None or data['price'] < 0:
        return jsonify({'error': 'Price must be a non-negative number'}), 400
    if data.get('stock') is not None and data['stock'] < 0:
        return jsonify({'error': 'Stock cannot be negative'}), 400

    product = Product(
        name=str(data['name']).strip(),
        description=data.get('description', ''),
        price=data['price'],
        stock=data.get('stock', 0)
    )
    db.session.add(product)
    db.session.commit()
    return jsonify(product.to_dict()), 201

@products_bp.route('/products/<int:product_id>', methods=['PUT'])
@token_required
@role_required('user', 'admin')
def update_product(current_user, product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    # Stronger validation
    if 'name' in data and (not data['name'] or len(str(data['name']).strip()) < 1):
        return jsonify({'error': 'Name cannot be empty'}), 400
    if 'price' in data and (data['price'] is None or data['price'] < 0):
        return jsonify({'error': 'Price must be a non-negative number'}), 400
    if 'stock' in data and data['stock'] < 0:
        return jsonify({'error': 'Stock cannot be negative'}), 400

    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.price = data.get('price', product.price)
    product.stock = data.get('stock', product.stock)

    db.session.commit()
    return jsonify(product.to_dict())

@products_bp.route('/products/<int:product_id>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_product(current_user, product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted'}), 200
