"""Invoice services for business logic."""

from datetime import timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.invoices.invoice_numbering import generate_invoice_number
from apps.invoices.models import Invoice, InvoiceItem, Payment
from apps.orders.models import Order
from apps.orders.services import change_order_status
from apps.invoices.tasks import send_invoice_email


@transaction.atomic
def create_invoice_from_order(order, user):
    if order.status != Order.Status.DELIVERED:
        raise ValidationError('Invoice can only be generated for delivered orders')
    if hasattr(order, 'invoice'):
        raise ValidationError('Invoice already exists for this order')
    
    invoice = Invoice.objects.create(
        order=order,
        vendor=order.vendor,
        buyer=order.buyer,
        invoice_number=generate_invoice_number(),
        issue_date=timezone.now().date(),
        due_date=timezone.now().date() + timedelta(days=15),
        subtotal=order.subtotal,
        tax_amount=order.tax_amount,
        total_amount=order.total_amount,
    )
    
    for item in order.items.all():
        InvoiceItem.objects.create(
            invoice=invoice,
            product_name=item.product_name,
            product_sku=item.product_sku,
            unit_price=item.unit_price,
            quantity=item.quantity,
            line_total=item.line_total,
        )
    
    change_order_status(order, Order.Status.INVOICED, changed_by=user)
    send_invoice_email.delay(invoice.id)
    return invoice
  


@transaction.atomic
def record_payment(invoice, user, amount, method, reference_number=''):
    payment = Payment.objects.create(
        invoice=invoice, amount=amount, method=method,
        reference_number=reference_number, recorded_by=user
    )
    paid_total = sum((p.amount for p in invoice.payments.all()), Decimal('0'))
    if paid_total >= invoice.total_amount:
        invoice.status = Invoice.Status.PAID
        invoice.save(update_fields=['status', 'updated_at'])
    return payment