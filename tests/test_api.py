import pytest
import json
import jwt
from sqlalchemy import inspect
from app import create_app, db
from models import Category, Order, OrderItem, Product, User
import seed as seed_module
from werkzeug.security import generate_password_hash


@pytest.fixture
def demo_users():
    return [
        {'username': 'admin', 'password': 'admin123', 'role': 'admin'},
        {'username': 'customer1', 'password': 'customer123', 'role': 'customer'},
    ]


@pytest.fixture
def client(demo_users):
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret'
    })
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            seeded_users = [
                User(
                    username=spec['username'],
                    password_hash=generate_password_hash(spec['password']),
                    role=spec['role'],
                )
                for spec in demo_users
            ]
            db.session.add_all(seeded_users)
            db.session.commit()
            yield client
            db.drop_all()

@pytest.fixture
def admin_token(client):
    response = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'admin123'})
    return json.loads(response.data)['token']

@pytest.fixture
def customer_token(client):
    response = client.post('/api/v1/auth/login', json={'username': 'customer1', 'password': 'customer123'})
    return json.loads(response.data)['token']


def test_health_endpoint(client):
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'


def test_health_endpoint_root_alias(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_index_route_serves_frontend_shell(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'E-commerce Lite' in response.data
    assert b'id="app"' in response.data
    assert b'/static/css/styles.css' in response.data
    assert b'/static/js/app.js' in response.data

def test_create_app_does_not_duplicate_structured_log_handlers():
    config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret'
    }
    app_one = create_app(config)
    app_two = create_app(config)

    count_one = sum(1 for handler in app_one.logger.handlers if getattr(handler, 'name', '') == 'structured_stdout')
    count_two = sum(1 for handler in app_two.logger.handlers if getattr(handler, 'name', '') == 'structured_stdout')

    assert count_one == 1
    assert count_two == 1

def test_ready_endpoint(client):
    response = client.get('/api/v1/ready')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ready'


def test_ready_endpoint_root_alias(client):
    response = client.get('/ready')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ready'


def test_login_success(client):
    response = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'admin123'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'token' in data

def test_login_token_contains_role_claim(client):
    response = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'admin123'})
    assert response.status_code == 200
    data = json.loads(response.data)

    payload = jwt.decode(data['token'], 'test-secret', algorithms=['HS256'])
    assert payload['role'] == 'admin'

def test_login_customer_success(client, customer_token):
    assert customer_token

def test_login_invalid_credentials(client):
    response = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'wrong'})
    assert response.status_code == 401

def test_login_nonexistent_user(client):
    response = client.post('/api/v1/auth/login', json={'username': 'nobody', 'password': 'test'})
    assert response.status_code == 401

def test_login_invalid_json(client):
    response = client.post('/api/v1/auth/login', data='not-json', content_type='application/json')
    assert response.status_code == 400


def test_register_success_returns_customer_token(client):
    response = client.post(
        '/api/v1/auth/register',
        json={'username': 'newshopper_reg', 'password': 'secret12'},
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'token' in data
    payload = jwt.decode(data['token'], 'test-secret', algorithms=['HS256'])
    assert payload['role'] == 'customer'


def test_register_duplicate_username(client):
    username = 'dup_reg_user'
    first = client.post(
        '/api/v1/auth/register',
        json={'username': username, 'password': 'pw123456'},
    )
    assert first.status_code == 201

    second = client.post(
        '/api/v1/auth/register',
        json={'username': username, 'password': 'different1'},
    )
    assert second.status_code == 409
    assert 'taken' in json.loads(second.data)['error'].lower()


def test_register_short_password(client):
    response = client.post(
        '/api/v1/auth/register',
        json={'username': 'goodname_user', 'password': 'abcde'},
    )
    assert response.status_code == 400


def test_register_short_username(client):
    response = client.post(
        '/api/v1/auth/register',
        json={'username': 'ab', 'password': 'validpw1'},
    )
    assert response.status_code == 400


def test_register_invalid_username_chars(client):
    response = client.post(
        '/api/v1/auth/register',
        json={'username': 'no!symbols', 'password': 'validpw1'},
    )
    assert response.status_code == 400


def test_register_invalid_json(client):
    response = client.post('/api/v1/auth/register', data='bad', content_type='application/json')
    assert response.status_code == 400


def test_create_product_admin_success(client, admin_token):
    response = client.post('/api/v1/products',
        json={
            'name': 'Laptop',
            'price': 999.99,
            'stock': 10
        },
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == 'Laptop'


def test_create_product_customer_forbidden(client, customer_token):
    response = client.post('/api/v1/products',
        json={
            'name': 'Laptop',
            'price': 999.99,
            'stock': 10
        },
        headers={'Authorization': f'Bearer {customer_token}'}
    )
    assert response.status_code == 403

def test_create_product_unauthenticated(client):
    response = client.post('/api/v1/products',
        json={
            'name': 'Laptop',
            'price': 999.99,
            'stock': 10
        }
    )
    assert response.status_code == 401

def test_get_products(client):
    response = client.get('/api/v1/products')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'products' in data

def test_get_product_by_id(client):
    with client.application.app_context():
        product = Product(name='Detail Product', description='Product detail route', price=15.75, stock=4)
        db.session.add(product)
        db.session.commit()
        product_id = product.id

    response = client.get(f'/api/v1/products/{product_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == product_id
    assert data['name'] == 'Detail Product'
    assert data['price'] == 15.75

def test_create_product_missing_fields(client, admin_token):
    response = client.post('/api/v1/products',
        json={'name': 'Incomplete'},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 400

def test_create_product_invalid_json(client, admin_token):
    response = client.post('/api/v1/products', data='not-json', content_type='application/json',
        headers={'Authorization': f'Bearer {admin_token}'})
    assert response.status_code == 400

def test_create_product_rejects_string_price_with_400(client, admin_token):
    response = client.post('/api/v1/products',
        json={
            'name': 'Laptop',
            'price': '9.99',
            'stock': 10
        },
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'Price must be a non-negative number'

def test_delete_product_admin_success(client, admin_token):
    client.post('/api/v1/products',
        json={'name': 'Test', 'price': 10.00},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    response = client.delete('/api/v1/products/1',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 200

def test_delete_product_customer_forbidden(client, customer_token):
    response = client.delete('/api/v1/products/1',
        headers={'Authorization': f'Bearer {customer_token}'}
    )
    assert response.status_code == 403

def test_delete_product_requires_auth(client):
    response = client.delete('/api/v1/products/1')
    assert response.status_code == 401

def test_update_product_admin_success(client, admin_token):
    client.post('/api/v1/products',
        json={'name': 'Test', 'price': 10.00},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    response = client.put('/api/v1/products/1',
        json={'name': 'Updated'},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 200


def test_update_product_customer_forbidden(client, customer_token, admin_token):
    client.post('/api/v1/products',
        json={'name': 'Test', 'price': 10.00},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    response = client.put('/api/v1/products/1',
        json={'name': 'Updated'},
        headers={'Authorization': f'Bearer {customer_token}'}
    )
    assert response.status_code == 403


def test_get_categories_empty(client):
    response = client.get('/api/v1/categories')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data == []

def test_create_category_admin(client, admin_token):
    response = client.post('/api/v1/categories',
        json={'name': 'Electronics', 'description': 'Electronic devices'},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == 'Electronics'

def test_create_category_duplicate(client, admin_token):
    client.post('/api/v1/categories',
        json={'name': 'Electronics'},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    response = client.post('/api/v1/categories',
        json={'name': 'Electronics'},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 409

def test_create_category_unauthenticated(client):
    response = client.post('/api/v1/categories', json={'name': 'Test'})
    assert response.status_code == 401

def test_delete_category_admin(client, admin_token):
    client.post('/api/v1/categories',
        json={'name': 'ToDelete'},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    response = client.delete('/api/v1/categories/1',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 200

def test_update_category_admin(client, admin_token):
    create_response = client.post('/api/v1/categories',
        json={'name': 'Update Me', 'description': 'Before'},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    category_id = json.loads(create_response.data)['id']

    response = client.put(f'/api/v1/categories/{category_id}',
        json={'name': 'Updated Category', 'description': 'After'},
        headers={'Authorization': f'Bearer {admin_token}'}
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'Updated Category'
    assert data['description'] == 'After'

def test_update_category_customer_forbidden(client, customer_token, admin_token):
    create_response = client.post('/api/v1/categories',
        json={'name': 'Admin Only Category'},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    category_id = json.loads(create_response.data)['id']

    response = client.put(f'/api/v1/categories/{category_id}',
        json={'name': 'Customer Edit Attempt'},
        headers={'Authorization': f'Bearer {customer_token}'}
    )

    assert response.status_code == 403


def test_order_domain_tables_and_relationships_exist(client):
    inspector = inspect(db.engine)
    table_names = set(inspector.get_table_names())

    assert {'categories', 'products', 'users', 'orders', 'order_items'}.issubset(table_names)

    with client.application.app_context():
        category = Category(name='Testing', description='Task 2 category')
        product = Product(
            name='Task 2 Product',
            description='Relationship coverage',
            price=49.99,
            stock=5,
            category=category,
        )
        customer = User(username='customer_task2', password_hash='hash', role='customer')
        order = Order(user=customer, status='pending_payment', total_amount=99.98)
        item = OrderItem(order=order, product=product, quantity=2, unit_price=49.99)

        db.session.add_all([category, product, customer, order, item])
        db.session.commit()

        assert product.category_id == category.id
        assert category.products[0].id == product.id
        assert customer.orders[0].id == order.id
        assert order.items[0].id == item.id
        assert item.product_id == product.id

        order_data = order.to_dict()
        assert order_data['user_id'] == customer.id
        assert order_data['status'] == 'pending_payment'
        assert order_data['total_amount'] == 99.98
        assert order_data['items'][0]['product_id'] == product.id
        assert order_data['items'][0]['line_total'] == 99.98
        assert product.to_dict()['category_id'] == category.id

    response = client.get('/api/v1/orders')
    assert response.status_code == 401


def test_product_delete_preserves_order_history(client):
    with client.application.app_context():
        category = Category(name='Deletion Safety', description='Task 2 regression')
        product = Product(
            name='Archived Product',
            description='Will be deleted',
            price=15.50,
            stock=1,
            category=category,
        )
        customer = User(username='customer_delete_case', password_hash='hash', role='customer')
        order = Order(user=customer, status='paid', total_amount=15.50)
        item = OrderItem(
            order=order,
            product=product,
            product_name=product.name,
            quantity=1,
            unit_price=15.50,
        )

        db.session.add_all([category, product, customer, order, item])
        db.session.commit()

        db.session.delete(product)
        db.session.commit()

        persisted_item = db.session.get(OrderItem, item.id)
        assert persisted_item is not None
        assert persisted_item.product_id is None
        assert persisted_item.product is None
        assert persisted_item.product_name == 'Archived Product'

        order_data = db.session.get(Order, order.id).to_dict()
        assert order_data['items'][0]['product_id'] is None
        assert order_data['items'][0]['product_name'] == 'Archived Product'


def test_seed_backfills_existing_task1_state(monkeypatch):
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret'
    })

    monkeypatch.setattr(seed_module, 'create_app', lambda: app)

    with app.app_context():
        db.create_all()
        db.session.add(User(username='admin', password_hash='legacy-hash', role='admin'))
        db.session.add(Product(name='Laptop', description='Legacy', price=999.99, stock=2))
        db.session.commit()

    seed_module.seed()
    seed_module.seed()

    with app.app_context():
        assert User.query.filter_by(username='admin').count() == 1
        assert User.query.filter_by(username='customer1').count() == 1
        assert Category.query.count() == 4
        assert Product.query.count() == 8

        laptop = Product.query.filter_by(name='Laptop').one()
        assert laptop.category is not None
        assert laptop.category.name == 'Electronics'


def test_customer_order_creation_success(client, customer_token):
    with client.application.app_context():
        product = Product(name='Orderable Laptop', description='Task 3 order', price=999.99, stock=5)
        db.session.add(product)
        db.session.commit()
        product_id = product.id

    response = client.post('/api/v1/orders',
        json={
            'items': [
                {'product_id': product_id, 'quantity': 2}
            ]
        },
        headers={'Authorization': f'Bearer {customer_token}'}
    )

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['status'] == 'pending_payment'
    assert data['total_amount'] == 1999.98
    assert len(data['items']) == 1
    assert data['items'][0]['product_id'] == product_id
    assert data['items'][0]['quantity'] == 2
    assert data['items'][0]['product_name'] == 'Orderable Laptop'
    assert data['items'][0]['line_total'] == 1999.98

    with client.application.app_context():
        product = db.session.get(Product, product_id)
        assert product.stock == 3


def test_customer_order_creation_insufficient_stock(client, customer_token):
    with client.application.app_context():
        product = Product(name='Low Stock Item', description='Task 3 stock', price=25.00, stock=1)
        db.session.add(product)
        db.session.commit()
        product_id = product.id

    response = client.post('/api/v1/orders',
        json={
            'items': [
                {'product_id': product_id, 'quantity': 2}
            ]
        },
        headers={'Authorization': f'Bearer {customer_token}'}
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'Insufficient stock for product Low Stock Item'


def test_customer_order_creation_empty_object_uses_validator_error(client, customer_token):
    response = client.post('/api/v1/orders',
        json={},
        headers={'Authorization': f'Bearer {customer_token}'}
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'Order items are required'


def test_customer_own_orders_listing_success(client, customer_token):
    with client.application.app_context():
        customer = User.query.filter_by(username='customer1').one()
        customer_id = customer.id
        other_customer = User(username='customer2', password_hash='hash', role='customer')
        product = Product(name='Own Orders Product', description='Task 3 list mine', price=40.00, stock=10)
        db.session.add_all([other_customer, product])
        db.session.flush()

        own_order = Order(user=customer, status='pending_payment', total_amount=80.00)
        own_item = OrderItem(order=own_order, product=product, quantity=2, unit_price=40.00)
        other_order = Order(user=other_customer, status='pending_payment', total_amount=40.00)
        other_item = OrderItem(order=other_order, product=product, quantity=1, unit_price=40.00)

        db.session.add_all([own_order, own_item, other_order, other_item])
        db.session.commit()

    response = client.get('/api/v1/orders/mine',
        headers={'Authorization': f'Bearer {customer_token}'}
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['orders']) == 1
    assert data['orders'][0]['user_id'] == customer_id
    assert data['orders'][0]['total_amount'] == 80.0
    assert data['orders'][0]['items'][0]['line_total'] == 80.0


def test_admin_forbidden_from_customer_order_listing(client, admin_token):
    response = client.get('/api/v1/orders/mine',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 403


def test_admin_all_orders_listing_success(client, admin_token):
    with client.application.app_context():
        customer = User.query.filter_by(username='customer1').one()
        product = Product(name='Admin Orders Product', description='Task 3 list all', price=12.50, stock=10)
        db.session.add(product)
        db.session.flush()

        order_one = Order(user=customer, status='pending_payment', total_amount=12.50)
        order_two = Order(user=customer, status='paid', total_amount=25.00)
        item_one = OrderItem(order=order_one, product=product, quantity=1, unit_price=12.50)
        item_two = OrderItem(order=order_two, product=product, quantity=2, unit_price=12.50)

        db.session.add_all([order_one, order_two, item_one, item_two])
        db.session.commit()

    response = client.get('/api/v1/orders',
        headers={'Authorization': f'Bearer {admin_token}'}
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['orders']) == 2
    assert {order['status'] for order in data['orders']} == {'pending_payment', 'paid'}
    assert {order['items'][0]['line_total'] for order in data['orders']} == {12.5, 25.0}


def test_simulate_payment_success(client, customer_token):
    with client.application.app_context():
        product = Product(name='Pay Simulation Item', description='pay demo', price=12.50, stock=5)
        db.session.add(product)
        db.session.commit()
        product_id = product.id

    create = client.post(
        '/api/v1/orders',
        json={'items': [{'product_id': product_id, 'quantity': 1}]},
        headers={'Authorization': f'Bearer {customer_token}'},
    )
    assert create.status_code == 201
    order_id = json.loads(create.data)['id']
    assert json.loads(create.data)['status'] == 'pending_payment'

    pay = client.post(
        f'/api/v1/orders/{order_id}/simulate-payment',
        headers={'Authorization': f'Bearer {customer_token}'},
    )
    assert pay.status_code == 200
    data = json.loads(pay.data)
    assert data['status'] == 'paid'


def test_simulate_payment_idempotent_conflict(client, customer_token):
    with client.application.app_context():
        product = Product(name='Paid Twice Guard', description='guard', price=5.00, stock=5)
        db.session.add(product)
        db.session.commit()
        product_id = product.id

    create = client.post(
        '/api/v1/orders',
        json={'items': [{'product_id': product_id, 'quantity': 1}]},
        headers={'Authorization': f'Bearer {customer_token}'},
    )
    order_id = json.loads(create.data)['id']

    assert client.post(
        f'/api/v1/orders/{order_id}/simulate-payment',
        headers={'Authorization': f'Bearer {customer_token}'},
    ).status_code == 200

    second = client.post(
        f'/api/v1/orders/{order_id}/simulate-payment',
        headers={'Authorization': f'Bearer {customer_token}'},
    )
    assert second.status_code == 400
    body = json.loads(second.data)
    assert 'not awaiting payment' in body['error'].lower()


def test_simulate_payment_forbidden_other_customer(client, customer_token):
    with client.application.app_context():
        other = User(
            username='customer_other_pay',
            password_hash=generate_password_hash('pwd123'),
            role='customer',
        )
        product = Product(name='Other Pay Product', description='demo', price=15.00, stock=10)
        db.session.add_all([other, product])
        db.session.commit()
        product_id = product.id

    create = client.post(
        '/api/v1/orders',
        json={'items': [{'product_id': product_id, 'quantity': 1}]},
        headers={'Authorization': f'Bearer {customer_token}'},
    )
    order_id = json.loads(create.data)['id']

    login_other = client.post(
        '/api/v1/auth/login',
        json={'username': 'customer_other_pay', 'password': 'pwd123'},
    )
    assert login_other.status_code == 200
    other_token = json.loads(login_other.data)['token']

    forbidden = client.post(
        f'/api/v1/orders/{order_id}/simulate-payment',
        headers={'Authorization': f'Bearer {other_token}'},
    )
    assert forbidden.status_code == 403


def test_simulate_payment_admin_role_forbidden(client, admin_token):
    response = client.post(
        '/api/v1/orders/1/simulate-payment',
        headers={'Authorization': f'Bearer {admin_token}'},
    )
    assert response.status_code == 403


def test_customer_forbidden_from_admin_order_listing(client, customer_token):
    response = client.get('/api/v1/orders',
        headers={'Authorization': f'Bearer {customer_token}'}
    )
    assert response.status_code == 403
