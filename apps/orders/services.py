"""Order services for business logic."""

import random
import string
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.catalog.models import Product
from apps.orders.models import Address, Order, OrderItem, OrderStatusHistory
from apps.orders.state_machine import can_transition
from apps.vendors.models import VendorProfile
from decimal import Decimal


def generate_order_number():
    while True:
        number = f"ORD-{timezone.now().year}-{''.join(random.choices(string.digits, k=5))}"
        if not Order.objects.filter(order_number=number).exists():
            return number

def calculate_order_totals(order):
    subtotal = sum(item.line_total for item in order.items.all())
    tax_amount = round(subtotal * Decimal('0.18'), 2)
    order.subtotal = subtotal
    order.tax_amount = tax_amount
    order.total_amount = subtotal + tax_amount + order.shipping_charge - order.discount_amount
    order.save()
    return order


def change_order_status(order, to_status, changed_by=None, remarks=''):
    if not can_transition(order.status, to_status):
        raise ValidationError(f'Invalid transition from {order.status} to {to_status}')
    from_status = order.status
    order.status = to_status
    order.save(update_fields=['status', 'updated_at'])
    OrderStatusHistory.objects.create(
        order=order, from_status=from_status, to_status=to_status,
        changed_by=changed_by, remarks=remarks
    )
    return order


def reserve_stock(order):
    for item in order.items.all():
        product = Product.objects.select_for_update().get(id=item.product_id)
        if product.stock_quantity < item.quantity:
            raise ValidationError(f'Insufficient stock for {product.name}')
        product.stock_quantity -= item.quantity
        product.save(update_fields=['stock_quantity', 'updated_at'])


def release_stock(order):
    for item in order.items.all():
        product = Product.objects.select_for_update().get(id=item.product_id)
        product.stock_quantity += item.quantity
        product.save(update_fields=['stock_quantity', 'updated_at'])


@transaction.atomic
def create_order(*, buyer, vendor_id, shipping_address_id, billing_address_id, items, notes=''):
    vendor = VendorProfile.objects.get(id=vendor_id)
    shipping = Address.objects.get(id=shipping_address_id, user=buyer)
    billing = Address.objects.get(id=billing_address_id, user=buyer)
    
    order = Order.objects.create(
        buyer=buyer, vendor=vendor,
        shipping_address=shipping, billing_address=billing,
        status=Order.Status.DRAFT, notes=notes,
    )
    order.order_number = generate_order_number()
    order.save()
    
    for item in items:
        product = Product.objects.select_for_update().get(id=item['product'], vendor=vendor)
        if product.stock_quantity < item['quantity']:
            raise ValidationError(f'Insufficient stock for {product.name}')
        OrderItem.objects.create(
            order=order, product=product,
            product_name=product.name, product_sku=product.sku,
            unit_price=product.price, quantity=item['quantity'],
            line_total=product.price * item['quantity'],
        )
    
    calculate_order_totals(order)
    change_order_status(order, Order.Status.PENDING_APPROVAL, changed_by=buyer)
    return order


@transaction.atomic
def approve_order(order, user, remarks=''):
    change_order_status(order, Order.Status.APPROVED, changed_by=user, remarks=remarks)
    order.approved_by = user
    order.approved_at = timezone.now()
    order.save()
    reserve_stock(order)
    return order


@transaction.atomic
def cancel_order(order, user, remarks=''):
    if order.status in ['approved', 'sent_to_vendor', 'accepted_by_vendor']:
        release_stock(order)
    change_order_status(order, Order.Status.CANCELLED, changed_by=user, remarks=remarks)
    return order


def update_status_with_role(order, to_status, user, remarks=''):
    allowed = user.role == 'admin' or user.is_staff
    if not allowed and hasattr(user, 'vendor_profile') and order.vendor == user.vendor_profile:
        allowed = to_status in ['accepted_by_vendor', 'partially_delivered', 'delivered', 'invoiced']
    if not allowed and order.buyer == user:
        allowed = to_status in ['cancelled']
    if not allowed:
        raise ValidationError('You are not allowed to perform this status change')
    if to_status == 'cancelled':
        return cancel_order(order, user, remarks)
    return change_order_status(order, to_status, changed_by=user, remarks=remarks)