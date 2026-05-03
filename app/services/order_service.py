from decimal import Decimal

from app.extensions import db
from app.services.validators import NotFoundError, ServiceError, ValidationError
from models import Order, OrderItem, Product


def create_order(user, data):
    """Build an order from cart items, deducting stock as we go.

    Uses an explicit transaction boundary (try/except + rollback) so that
    if any step fails the entire operation is rolled back atomically.
    """
    product_ids = [item['product_id'] for item in data['items']]
    products = Product.query.filter(Product.id.in_(product_ids)).all()
    products_by_id = {product.id: product for product in products}

    order = Order(user=user, status='pending_payment', total_amount=Decimal('0.00'))
    db.session.add(order)

    try:
        total_amount = Decimal('0.00')
        for item in data['items']:
            product = products_by_id.get(item['product_id'])
            if product is None:
                raise NotFoundError(f"Product {item['product_id']} not found")

            quantity = item['quantity']
            if product.stock < quantity:
                raise ValidationError(f'Insufficient stock for product {product.name}')

            product.stock -= quantity
            unit_price = Decimal(str(product.price))
            total_amount += unit_price * quantity
            db.session.add(
                OrderItem(
                    order=order,
                    product=product,
                    product_name=product.name,
                    quantity=quantity,
                    unit_price=unit_price,
                )
            )

        order.total_amount = total_amount
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return order


def list_orders_for_user(user):
    return (
        Order.query
        .filter_by(user_id=user.id)
        .order_by(Order.created_at.desc(), Order.id.desc())
        .all()
    )


def list_all_orders():
    # NOTE: no pagination — fine for demo size, but will be slow with thousands of orders
    return Order.query.order_by(Order.created_at.desc(), Order.id.desc()).all()


def simulate_payment(user, order_id):
    order = Order.query.get(order_id)
    if order is None:
        raise NotFoundError(f'Order {order_id} not found')
    if order.user_id != user.id:
        raise ServiceError('Not your order', status_code=403)
    if order.status != 'pending_payment':
        raise ValidationError(f'Order is not awaiting payment (status={order.status})')

    order.status = 'paid'
    db.session.commit()
    return order
