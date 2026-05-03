import pytest
from decimal import Decimal

from werkzeug.security import generate_password_hash

from app import create_app, db
from models import Category, Order, Product, User


@pytest.fixture
def app_ctx():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret',
    })
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def sample_category(app_ctx):
    cat = Category(name='Electronics', description='Electronic devices')
    db.session.add(cat)
    db.session.commit()
    return cat


@pytest.fixture
def sample_product(app_ctx):
    prod = Product(name='Test Laptop', description='A test product', price=Decimal('999.99'), stock=10)
    db.session.add(prod)
    db.session.commit()
    return prod


class TestCatalogService:
    def test_create_product_stores_data(self, app_ctx):
        from app.services.catalog_service import create_product

        data = {'name': 'New Product', 'price': 49.99, 'stock': 5}
        product = create_product(data)
        assert product is not None
        assert product.name == 'New Product'
        assert float(product.price) == 49.99

    def test_update_product_changes_fields(self, app_ctx, sample_product):
        from app.services.catalog_service import update_product

        updated = update_product(sample_product, {'name': 'Updated', 'price': 25.00})
        assert updated.name == 'Updated'
        assert float(updated.price) == 25.00

    def test_delete_product_removes_from_db(self, app_ctx, sample_product):
        from app.services.catalog_service import delete_product

        pid = sample_product.id
        delete_product(sample_product)
        remaining = Product.query.get(pid)
        assert remaining is None

    def test_create_category_raises_conflict_on_duplicate(self, app_ctx):
        from app.services.catalog_service import ConflictError, create_category

        create_category({'name': 'Duplicate'})
        with pytest.raises(ConflictError):
            create_category({'name': 'Duplicate'})

    def test_update_category_name_with_conflict(self, app_ctx):
        from app.services.catalog_service import ConflictError, update_category

        cat_a = Category(name='Category A')
        cat_b = Category(name='Category B')
        db.session.add_all([cat_a, cat_b])
        db.session.commit()
        with pytest.raises(ConflictError):
            update_category(cat_a, {'name': 'Category B'})

    def test_delete_category_removes_from_db(self, app_ctx, sample_category):
        from app.services.catalog_service import delete_category

        cid = sample_category.id
        delete_category(sample_category)
        remaining = Category.query.get(cid)
        assert remaining is None


class TestOrderService:
    def test_create_order_deducts_stock(self, app_ctx):
        from app.services.order_service import create_order

        product = Product(name='Stock Item', price=Decimal('10.00'), stock=5)
        db.session.add(product)
        db.session.commit()
        customer = User(username='buyer', password_hash=generate_password_hash('pw123'), role='customer')
        db.session.add(customer)
        db.session.flush()

        order = create_order(customer, {'items': [{'product_id': product.id, 'quantity': 2}]})
        assert order.status == 'pending_payment'
        assert float(order.total_amount) == 20.00
        assert product.stock == 3

    def test_create_order_rejects_insufficient_stock(self, app_ctx):
        from app.services.order_service import create_order
        from app.services.validators import ValidationError

        product = Product(name='Low Stock', price=Decimal('5.00'), stock=1)
        db.session.add(product)
        db.session.commit()
        customer = User(username='buyer2', password_hash=generate_password_hash('pw123'), role='customer')
        db.session.add(customer)
        db.session.flush()

        with pytest.raises(ValidationError):
            create_order(customer, {'items': [{'product_id': product.id, 'quantity': 5}]})

    def test_list_orders_for_user_filters_correctly(self, app_ctx):
        from app.services.order_service import list_orders_for_user

        customer = User(username='orderer', password_hash=generate_password_hash('pw123'), role='customer')
        other = User(username='other', password_hash=generate_password_hash('pw123'), role='customer')
        db.session.add_all([customer, other])
        db.session.flush()

        order1 = Order(user=customer, status='pending_payment', total_amount=Decimal('10.00'))
        order2 = Order(user=other, status='paid', total_amount=Decimal('20.00'))
        db.session.add_all([order1, order2])
        db.session.commit()

        my_orders = list_orders_for_user(customer)
        assert len(my_orders) == 1
        assert my_orders[0].user_id == customer.id


class TestAuthService:
    def test_register_user_creates_customer(self, app_ctx):
        from app.services.auth_service import register_user

        user = register_user('newreguser', 'password123')
        assert user is not None
        assert user.role == 'customer'
        assert user.username == 'newreguser'

    def test_register_duplicate_raises_conflict(self, app_ctx):
        from app.services.auth_service import ConflictError, register_user

        register_user('dupuser1', 'password123')
        with pytest.raises(ConflictError):
            register_user('dupuser1', 'differentpw')

    def test_register_short_password_raises_validation_error(self, app_ctx):
        from app.services.auth_service import ValidationError, register_user

        with pytest.raises(ValidationError):
            register_user('shortpwuser', 'abc')
