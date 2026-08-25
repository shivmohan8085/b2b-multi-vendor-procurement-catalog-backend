"""Seed demo addresses and orders."""

from apps.accounts.models import User
from apps.catalog.models import Product
from apps.orders import services
from apps.orders.models import Address, Order


def seed():
    admin = User.objects.get(email='shivbhatt0111@gmail.com')
    buyer1 = User.objects.get(email='shivbhatt0112@gmail.com')
    buyer2 = User.objects.get(email='shivbhatt0112@gmail.com')
    
    addr1, _ = Address.objects.get_or_create(
        user=buyer1, pincode='400001',
        defaults={'contact_person': 'Rahul Sharma', 'phone': '+911234567890', 'address_line1': '123 Business Park', 'city': 'Mumbai', 'state': 'Maharashtra', 'is_default': True}
    )
    addr2, _ = Address.objects.get_or_create(
        user=buyer2, pincode='110001',
        defaults={'contact_person': 'Priya Patel', 'phone': '+919876543210', 'address_line1': '456 Corporate Hub', 'city': 'Delhi', 'state': 'Delhi', 'is_default': True}
    )
    
    created = 0
    if not Order.objects.filter(buyer=buyer1).exists():
        mouse = Product.objects.get(sku='WM-001')
        keyboard = Product.objects.get(sku='MK-001')
        order1 = services.create_order(
            buyer=buyer1, vendor_id=mouse.vendor_id,
            shipping_address_id=addr1.id, billing_address_id=addr1.id,
            items=[{'product': mouse.id, 'quantity': 10}, {'product': keyboard.id, 'quantity': 5}],
            notes='First demo order',
        )
        services.approve_order(order1, admin, 'Approved via seed')
        created += 1
    
    if not Order.objects.filter(buyer=buyer2).exists():
        paper = Product.objects.get(sku='AP-100')
        services.create_order(
            buyer=buyer2, vendor_id=paper.vendor_id,
            shipping_address_id=addr2.id, billing_address_id=addr2.id,
            items=[{'product': paper.id, 'quantity': 50}],
        )
        created += 1
    
    return f'{created} orders seeded'