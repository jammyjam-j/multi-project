from app import create_app, db
from models import Category, Product, User
from werkzeug.security import generate_password_hash


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        user_specs = [
            {'username': 'admin', 'password': 'admin123', 'role': 'admin'},
            {'username': 'customer1', 'password': 'customer123', 'role': 'customer'},
        ]
        users = []
        for spec in user_specs:
            user = User.query.filter_by(username=spec['username']).first()
            if user is None:
                user = User(username=spec['username'])
                db.session.add(user)
            user.password_hash = generate_password_hash(spec['password'])
            user.role = spec['role']
            users.append(user)

        category_specs = [
            {'name': 'Electronics', 'description': 'Electronic devices and accessories'},
            {'name': 'Peripherals', 'description': 'Mouse, keyboards, and other peripherals'},
            {'name': 'Audio', 'description': 'Headphones, speakers, and audio equipment'},
            {'name': 'Accessories', 'description': 'Cables, hubs, and desk accessories'},
        ]
        categories = []
        categories_by_name = {}
        for spec in category_specs:
            category = Category.query.filter_by(name=spec['name']).first()
            if category is None:
                category = Category(name=spec['name'])
                db.session.add(category)
            category.description = spec['description']
            categories.append(category)
            categories_by_name[spec['name']] = category

        db.session.flush()

        product_specs = [
            {
                'name': 'Laptop',
                'description': 'High-performance laptop',
                'price': 999.99,
                'stock': 50,
                'category_name': 'Electronics',
            },
            {
                'name': 'Mouse',
                'description': 'Wireless ergonomic mouse',
                'price': 29.99,
                'stock': 200,
                'category_name': 'Peripherals',
            },
            {
                'name': 'Keyboard',
                'description': 'Mechanical keyboard',
                'price': 79.99,
                'stock': 150,
                'category_name': 'Peripherals',
            },
            {
                'name': 'Monitor',
                'description': '27-inch 4K display',
                'price': 399.99,
                'stock': 75,
                'category_name': 'Electronics',
            },
            {
                'name': 'Headphones',
                'description': 'Noise-cancelling headphones',
                'price': 149.99,
                'stock': 100,
                'category_name': 'Audio',
            },
            {
                'name': 'USB-C Hub',
                'description': 'Multi-port USB-C hub',
                'price': 49.99,
                'stock': 300,
                'category_name': 'Accessories',
            },
            {
                'name': 'Webcam',
                'description': '1080p HD webcam',
                'price': 69.99,
                'stock': 120,
                'category_name': 'Electronics',
            },
            {
                'name': 'Desk Lamp',
                'description': 'LED desk lamp with dimmer',
                'price': 34.99,
                'stock': 80,
                'category_name': 'Accessories',
            },
        ]
        products = []
        for spec in product_specs:
            product = Product.query.filter_by(name=spec['name']).first()
            if product is None:
                product = Product(name=spec['name'])
                db.session.add(product)
            product.description = spec['description']
            product.price = spec['price']
            product.stock = spec['stock']
            product.category = categories_by_name[spec['category_name']]
            products.append(product)

        db.session.commit()
        print(f"Seeded/backfilled {len(users)} users, {len(categories)} categories, and {len(products)} products successfully.")

if __name__ == '__main__':
    seed()
