"""Celery tasks for invoices."""

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage


@shared_task
def send_invoice_email(invoice_id):
    from apps.invoices.models import Invoice
    from apps.invoices.pdf_generator import generate_invoice_pdf
    
    invoice = Invoice.objects.select_related('order', 'vendor', 'buyer').get(id=invoice_id)
    
    if not invoice.pdf_file:
        generate_invoice_pdf(invoice)
    
    subject = f'Invoice {invoice.invoice_number} from {invoice.vendor.company_name}'
    body = (
        f'Hi {invoice.buyer.get_full_name() or invoice.buyer.email},\n\n'
        f'Please find attached invoice {invoice.invoice_number} for order {invoice.order.order_number}.\n\n'
        f'Total Amount: ₹{invoice.total_amount}\n'
        f'Due Date: {invoice.due_date}\n\n'
        f'Thanks,\nProcureFlow Team'
    )
    
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[invoice.buyer.email],
    )
    invoice.pdf_file.open('rb')
    email.attach(f'{invoice.invoice_number}.pdf', invoice.pdf_file.read(), 'application/pdf')
    invoice.pdf_file.close()
    email.send()
    return f'Invoice email sent for {invoice.invoice_number}'


@shared_task
def send_order_confirmation_email(order_id):
    from apps.orders.models import Order
    
    order = Order.objects.select_related('buyer', 'vendor').get(id=order_id)
    
    subject = f'Order Confirmed: {order.order_number}'
    body = (
        f'Hi {order.buyer.get_full_name() or order.buyer.email},\n\n'
        f'Your order {order.order_number} has been placed with {order.vendor.company_name}.\n\n'
        f'Total Amount: ₹{order.total_amount}\n'
        f'Items: {order.items.count()}\n\n'
        f'Thanks,\nProcureFlow Team'
    )
    
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.buyer.email],
    )
    email.send()
    return f'Order confirmation email sent for {order.order_number}'