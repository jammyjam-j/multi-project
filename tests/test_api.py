import pytest
import json
from app import create_app, db
from models import User
from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db',
        'SECRET_KEY': 'test-secret'
    })
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Seed a user for auth tests
            admin = User(username='admin', password_hash=generate_password_hash('admin123'), role='admin')
            db.session.add(admin)
            db.session.commit()
            yield client
            db.drop_all()

@pytest.fixture
def auth_token(client):
    """Return a valid JWT token."""
    response = client.post('/auth/login', json={'username': 'admin', 'password': 'admin123'})
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

def test_create_product(client, auth_token):
    response = client.post('/products',
        json={
            'name': 'Laptop',
            'price': 999.99,
            'stock': 10
        },
        headers={'Authorization': f'Bearer {auth_token}'}
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

def test_create_product_missing_fields(client, auth_token):
    response = client.post('/products',
        json={'name': 'Incomplete'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 400

def test_delete_nonexistent_product(client, auth_token):
    response = client.delete('/products/999',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 404

def test_delete_product_requires_auth(client):
    # First create a product with auth, then try deleting without auth
    # This tests that DELETE is protected
    response = client.delete('/products/1')
    assert response.status_code == 401
