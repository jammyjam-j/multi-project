from .auth_routes import auth_bp
from .health_routes import health_bp
from .order_routes import orders_bp
from .product_routes import categories_bp, products_bp

__all__ = [
    'auth_bp',
    'categories_bp',
    'health_bp',
    'orders_bp',
    'products_bp',
]
