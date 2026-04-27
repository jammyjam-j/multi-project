import pytest
import json
from app import create_app, db
from models import User
from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret'
    })
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Seed users with different roles
            admin = User(username='admin', password_hash=generate_password_hash('admin123'), role='admin')
            user = User(username='editor', password_hash=generate_password_hash('editor123'), role='user')
            viewer = User(username='viewer', password_hash=generate_password_hash('viewer123'), role='viewer')
            db.session.add_all([admin, user, viewer])
            db.session.commit()
            yield client
            db.drop_all()

@pytest.fixture
def admin_token(client):
    """Return a JWT token for the admin user."""
    response = client.post('/auth/login', json={'username': 'admin', 'password': 'admin123'})
    return json.loads(response.data)['token']

@pytest.fixture
def user_token(client):
    """Return a JWT token for the regular user."""
    response = client.post('/auth/login', json={'username': 'editor', 'password': 'editor123'})
    return json.loads(response.data)['token']

@pytest.fixture
def viewer_token(client):
    """Return a JWT token for the viewer user."""
    response = client.post('/auth/login', json={'username': 'viewer', 'password': 'viewer123'})
    return json.loads(response.data)['token']

def test_health_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_ready_endpoint(client):
    response = client.get('/ready')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ready'

def test_login_success(client):
    response = client.post('/auth/login', json={'username': 'admin', 'password': 'admin123'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'token' in data

def test_login_invalid_credentials(client):
    response = client.post('/auth/login', json={'username': 'admin', 'password': 'wrong'})
    assert response.status_code == 401

def test_login_nonexistent_user(client):
    response = client.post('/auth/login', json={'username': 'nobody', 'password': 'test'})
    assert response.status_code == 401

def test_create_product(client, user_token):
    response = client.post('/products',
        json={
            'name': 'Laptop',
            'price': 999.99,
            'stock': 10
        },
        headers={'Authorization': f'Bearer {user_token}'}
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == 'Laptop'

def test_create_product_unauthenticated(client):
    response = client.post('/products',
        json={
            'name': 'Laptop',
            'price': 999.99,
            'stock': 10
        }
    )
    assert response.status_code == 401

def test_get_products(client):
    response = client.get('/products')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'products' in data

def test_create_product_missing_fields(client, user_token):
    response = client.post('/products',
        json={'name': 'Incomplete'},
        headers={'Authorization': f'Bearer {user_token}'}
    )
    assert response.status_code == 400

def test_delete_product_admin_success(client, admin_token):
    # First create a product
    client.post('/products',
        json={'name': 'Test', 'price': 10.00},
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    # Then delete it as admin
    response = client.delete('/products/1',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 200

def test_delete_product_viewer_forbidden(client, viewer_token):
    response = client.delete('/products/1',
        headers={'Authorization': f'Bearer {viewer_token}'}
    )
    assert response.status_code == 403

def test_delete_product_requires_auth(client):
    response = client.delete('/products/1')
    assert response.status_code == 401

def test_update_product_user_success(client, user_token):
    # Create a product first
    client.post('/products',
        json={'name': 'Test', 'price': 10.00},
        headers={'Authorization': f'Bearer {user_token}'}
    )
    # Update as user
    response = client.put('/products/1',
        json={'name': 'Updated'},
        headers={'Authorization': f'Bearer {user_token}'}
    )
    assert response.status_code == 200

def test_update_product_viewer_forbidden(client, viewer_token):
    response = client.put('/products/1',
        json={'name': 'Updated'},
        headers={'Authorization': f'Bearer {viewer_token}'}
    )
    assert response.status_code == 403

def test_login_invalid_json(client):
    response = client.post('/auth/login', data='not-json', content_type='application/json')
    assert response.status_code == 400

def test_create_product_invalid_json(client, user_token):
    response = client.post('/products', data='not-json', content_type='application/json',
        headers={'Authorization': f'Bearer {user_token}'})
    assert response.status_code == 400
