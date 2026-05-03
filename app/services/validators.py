import re
from numbers import Number

_USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]+$')


class ServiceError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None):
        super().__init__(message)
        if status_code is not None:
            self.status_code = status_code
        self.message = message


class ValidationError(ServiceError):
    status_code = 400


class ConflictError(ServiceError):
    status_code = 409


class NotFoundError(ServiceError):
    status_code = 404


def _is_number(value):
    return isinstance(value, Number) and not isinstance(value, bool)


def validate_product_payload(data, require_name, require_price):
    errors = []

    if require_name and 'name' not in data:
        errors.append('Missing required fields: name, price')
    elif 'name' in data and not str(data.get('name', '')).strip():
        errors.append('Name cannot be empty')

    if require_price and 'price' not in data:
        if 'Missing required fields: name, price' not in errors:
            errors.append('Missing required fields: name, price')
    elif 'price' in data and (
        data['price'] is None
        or not _is_number(data['price'])
        or data['price'] < 0
    ):
        errors.append('Price must be a non-negative number')

    if 'stock' in data and (
        not _is_number(data['stock']) or data['stock'] < 0
    ):
        errors.append('Stock cannot be negative')

    return errors


def validate_registration_credentials(username, password):
    errors = []
    username_value = str(username or '').strip()

    if not username_value:
        errors.append('Username is required')
    elif len(username_value) < 3:
        errors.append('Username must be at least 3 characters')
    elif len(username_value) > 80:
        errors.append('Username is too long')
    elif not _USERNAME_PATTERN.match(username_value):
        errors.append('Username may only contain letters, numbers, and underscores')

    pwd = '' if password is None else str(password)
    if not pwd:
        errors.append('Password is required')
    elif len(pwd) < 6:
        errors.append('Password must be at least 6 characters')

    return errors


def validate_category_name(name):
    if name is None:
        return ''
    return str(name).strip()


def validate_category_payload(data, require_name):
    errors = []

    if require_name and 'name' not in data:
        errors.append('Name is required')
    elif 'name' in data and not validate_category_name(data.get('name')):
        errors.append('Name cannot be empty' if not require_name else 'Name is required')

    return errors


def validate_order_payload(data):
    errors = []

    if 'items' not in data:
        return ['Order items are required']

    items = data.get('items')
    if not isinstance(items, list) or not items:
        return ['Order must include at least one item']

    for item in items:
        if not isinstance(item, dict):
            return ['Each order item must be an object']
        if 'product_id' not in item or 'quantity' not in item:
            return ['Each order item requires product_id and quantity']
        # Note: booleans pass isinstance(x, int) in Python, but the <= 0 check catches them
        if not isinstance(item['product_id'], int) or item['product_id'] <= 0:
            return ['Product ID must be a positive integer']
        if not isinstance(item['quantity'], int) or item['quantity'] <= 0:
            return ['Quantity must be a positive integer']

    return errors
