"""Seed demo invoices with PDF."""

from apps.accounts.models import User
from apps.invoices import services
from apps.invoices.models import Invoice
from apps.invoices.pdf_generator import generate_invoice_pdf
from apps.orders.models import Order
from apps.orders.services import change_order_status


def seed():
    vendor_user = User.objects.get(email='shivbhatt0113@gmail.com')
    order = Order.objects.filter(buyer__email='shivbhatt0112@gmail.com').first()
    
    if not order or Invoice.objects.filter(order=order).exists():
        return '0 invoices seeded'
    
    for next_status in ['sent_to_vendor', 'accepted_by_vendor', 'delivered']:
        if order.status != next_status:
            change_order_status(order, next_status, changed_by=vendor_user)
    
    invoice = services.create_invoice_from_order(order, vendor_user)
    generate_invoice_pdf(invoice)
    return '1 invoice seeded with PDF'