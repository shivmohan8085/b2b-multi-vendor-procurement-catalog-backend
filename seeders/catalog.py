"""Seed demo categories, tags and products."""

from django.utils.text import slugify
from apps.catalog.models import Category, Tag, Product
from apps.vendors.models import VendorProfile

CATEGORIES = ['Electronics', 'Office Supplies', 'Furniture', 'IT Accessories']
TAGS = ['New Arrival', 'Bestseller', 'Bulk Deal']

PRODUCTS = [
    {'vendor_email': 'shivbhatt0113@gmail.com', 'category': 'Electronics', 'name': 'Wireless Mouse', 'sku': 'WM-001', 'price': '599.00', 'stock': 100},
    {'vendor_email': 'shivbhatt0113@gmail.com', 'category': 'Electronics', 'name': 'Mechanical Keyboard', 'sku': 'MK-001', 'price': '2499.00', 'stock': 50},
    {'vendor_email': 'shivbhatt0113@gmail.com', 'category': 'Office Supplies', 'name': 'A4 Paper Pack', 'sku': 'AP-100', 'price': '299.00', 'stock': 500},
    {'vendor_email': 'shivbhatt0113@gmail.com', 'category': 'Furniture', 'name': 'Office Chair', 'sku': 'OC-010', 'price': '4999.00', 'stock': 30},
]


def seed():
    for name in CATEGORIES:
        Category.objects.get_or_create(slug=slugify(name), defaults={'name': name})
    for name in TAGS:
        Tag.objects.get_or_create(slug=slugify(name), defaults={'name': name})
    
    for data in PRODUCTS:
        if Product.objects.filter(sku=data['sku']).exists():
            continue
        vendor = VendorProfile.objects.get(user__email=data['vendor_email'])
        product = Product.objects.create(
            vendor=vendor,
            category=Category.objects.get(name=data['category']),
            name=data['name'],
            slug=slugify(f"{data['name']}-{data['sku']}"),
            sku=data['sku'],
            description=f"High quality {data['name']} for business use",
            short_description=data['name'],
            price=data['price'],
            stock_quantity=data['stock'],
            status='active',
        )
        product.tags.add(Tag.objects.first())
    return f'{len(PRODUCTS)} products seeded'