from decimal import Decimal

from app.extensions import db
from app.services.cache_service import cache_invalidate
from app.services.validators import ConflictError
from models import Category, Product


PRODUCT_CACHE_PREFIX = 'products:'


def _invalidate_catalog_cache():
    """Invalidate product-related cache entries after mutations."""
    cache_invalidate(PRODUCT_CACHE_PREFIX)


def _as_decimal(value):
    """Convert anything numeric to Decimal — avoids float precision issues with money."""
    return Decimal(str(value))


def create_product(data):
    product = Product(
        name=str(data['name']).strip(),
        description=data.get('description', ''),
        price=_as_decimal(data['price']),
        stock=int(data.get('stock', 0)),
        category_id=data.get('category_id'),
    )
    db.session.add(product)
    db.session.commit()
    _invalidate_catalog_cache()
    return product


def update_product(product, data):
    if 'name' in data:
        product.name = str(data['name']).strip()
    if 'description' in data:
        product.description = data['description']
    if 'price' in data:
        product.price = _as_decimal(data['price'])
    if 'stock' in data:
        product.stock = int(data['stock'])
    if 'category_id' in data:
        product.category_id = data['category_id']

    db.session.commit()
    _invalidate_catalog_cache()
    return product


def delete_product(product):
    db.session.delete(product)
    db.session.commit()
    _invalidate_catalog_cache()


def create_category(data):
    name = str(data['name']).strip()
    existing = Category.query.filter_by(name=name).first()
    if existing:
        raise ConflictError('Category already exists')

    category = Category(name=name, description=data.get('description', ''))
    db.session.add(category)
    db.session.commit()
    return category


def update_category(category, data):
    if 'name' in data:
        new_name = str(data['name']).strip()
        existing = Category.query.filter(
            Category.name == new_name,
            Category.id != category.id,
        ).first()
        if existing:
            raise ConflictError('Category name already taken')
        category.name = new_name

    if 'description' in data:
        category.description = data['description']

    db.session.commit()
    return category


def delete_category(category):
    # TODO: check for products in this category before allowing deletion
    db.session.delete(category)
    db.session.commit()
