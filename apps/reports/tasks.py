"""Celery tasks for reports."""

from datetime import timedelta
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.db.models import Sum
from django.utils import timezone


@shared_task
def send_daily_sales_report():
    from apps.orders.models import Order
    
    yesterday = timezone.now().date() - timedelta(days=1)
    
    orders = Order.objects.filter(
        created_at__date=yesterday,
        status__in=['approved', 'delivered', 'completed', 'invoiced']
    )
    
    total_orders = orders.count()
    total_revenue = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    
    subject = f'Daily Sales Report - {yesterday}'
    body = (
        f'Daily Sales Report for {yesterday}\n\n'
        f'Total Orders: {total_orders}\n'
        f'Total Revenue: {total_revenue}\n\n'
        f'Regards,\nProcureFlow Analytics Team'
    )
    
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=['shivbhatt0111@gmail.com'],
    )
    email.send()
    return f'Daily report sent for {yesterday}'