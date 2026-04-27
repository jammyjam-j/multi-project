import pytest
import json
from app import create_app, db

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
            yield client
            db.drop_all()

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

def test_create_product(client):
    response = client.post('/products',
        json={
            'name': 'Laptop',
            'price': 999.99,
            'stock': 10
        }
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == 'Laptop'

def test_get_products(client):
    response = client.get('/products')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'products' in data

def test_create_product_missing_fields(client):
    response = client.post('/products', json={'name': 'Incomplete'})
    assert response.status_code == 400

def test_delete_nonexistent_product(client):
    response = client.delete('/products/999')
    assert response.status_code == 404
