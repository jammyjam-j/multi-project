"""Simple DTO classes."""


class ProductDTO:
    def __init__(self, product):
        self.id = product.id
        self.name = product.name
        self.description = product.description
        self.price = float(product.price)
        self.stock = product.stock
        self.category_id = product.category_id
        self.created_at = product.created_at.isoformat() if product.created_at else None
        self.updated_at = product.updated_at.isoformat() if product.updated_at else None

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'stock': self.stock,
            'category_id': self.category_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }


class CategoryDTO:
    def __init__(self, category):
        self.id = category.id
        self.name = category.name
        self.description = category.description
        self.created_at = category.created_at.isoformat() if category.created_at else None

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at,
        }


class OrderDTO:
    def __init__(self, order, include_items=True):
        self.id = order.id
        self.user_id = order.user_id
        self.status = order.status
        self.total_amount = float(order.total_amount)
        self.created_at = order.created_at.isoformat() if order.created_at else None
        self.items = []
        if include_items:
            for item in order.items:
                self.items.append({
                    'id': item.id,
                    'order_id': item.order_id,
                    'product_id': item.product_id,
                    'product_name': item.product_name,
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price),
                    'line_total': float(item.unit_price * item.quantity),
                })

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status,
            'total_amount': self.total_amount,
            'created_at': self.created_at,
            'items': self.items,
        }


class UserDTO:
    def __init__(self, user):
        self.id = user.id
        self.username = user.username
        self.role = user.role
        self.created_at = user.created_at.isoformat() if user.created_at else None

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'created_at': self.created_at,
        }
