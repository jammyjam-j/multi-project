"""Seed script to populate the database with sample data."""
from app import create_app, db
from models import Product, User

def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        # Check if data already exists
        if Product.query.count() > 0:
            print("Database already populated. Run with --force to reset.")
            return

        # Sample users
        users = [
            User(username='admin', password_hash='admin123', role='admin'),
            User(username='jane_doe', password_hash='password123', role='user'),
            User(username='viewer', password_hash='viewonly', role='viewer'),
        ]
        for user in users:
            db.session.add(user)

        # Sample products
        products = [
            Product(name='Laptop', description='High-performance laptop', price=999.99, stock=50),
            Product(name='Mouse', description='Wireless ergonomic mouse', price=29.99, stock=200),
            Product(name='Keyboard', description='Mechanical keyboard', price=79.99, stock=150),
            Product(name='Monitor', description='27-inch 4K display', price=399.99, stock=75),
            Product(name='Headphones', description='Noise-cancelling headphones', price=149.99, stock=100),
            Product(name='USB-C Hub', description='Multi-port USB-C hub', price=49.99, stock=300),
            Product(name='Webcam', description='1080p HD webcam', price=69.99, stock=120),
            Product(name='Desk Lamp', description='LED desk lamp with dimmer', price=34.99, stock=80),
        ]
        for product in products:
            db.session.add(product)

        db.session.commit()
        print(f"Seeded {len(users)} users and {len(products)} products successfully.")

if __name__ == '__main__':
    seed()
