"""Signal handlers for notifications."""

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.notifications.services import create_notification, notify_order_status_changed
from apps.notifications.models import Notification


@receiver(post_save, sender='orders.OrderStatusHistory')
def notify_on_status_change(sender, instance, created, **kwargs):
    if not created:
        return
    notify_order_status_changed(
        order=instance.order,
        new_status=instance.to_status,
        changed_by=instance.changed_by,
    )


@receiver(post_save, sender='vendors.VendorProfile')
def notify_on_vendor_approval(sender, instance, **kwargs):
    if instance.approval_status == 'approved' and instance.approved_at:
        create_notification(
            recipient=instance.user,
            notification_type=Notification.Type.VENDOR_APPROVED,
            title='Vendor Approved',
            message=f'Your vendor profile for {instance.company_name} has been approved.',
        )
    elif instance.approval_status == 'rejected' and instance.rejection_reason:
        create_notification(
            recipient=instance.user,
            notification_type=Notification.Type.VENDOR_REJECTED,
            title='Vendor Rejected',
            message=f'Your vendor profile was rejected. Reason: {instance.rejection_reason}',
        )


@receiver(post_save, sender='invoices.Invoice')
def notify_on_invoice_created(sender, instance, created, **kwargs):
    if not created:
        return
    create_notification(
        recipient=instance.buyer,
        notification_type=Notification.Type.INVOICE_CREATED,
        title=f'New Invoice: {instance.invoice_number}',
        message=f'Invoice {instance.invoice_number} of ₹{instance.total_amount} has been generated.',
        related_id=instance.invoice_number,
    )
    create_notification(
        recipient=instance.vendor.user,
        notification_type=Notification.Type.INVOICE_CREATED,
        title=f'Invoice Generated: {instance.invoice_number}',
        message=f'You generated invoice {instance.invoice_number} for ₹{instance.total_amount}.',
        related_id=instance.invoice_number,
    )