"""Notification services."""

from apps.notifications.models import Notification


def create_notification(recipient, notification_type, title, message, related_id=''):
    if not recipient:
        return None
    return Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        related_id=related_id,
    )


def notify_order_status_changed(order, new_status, changed_by):
    from apps.notifications.models import Notification
    recipients = set()
    if order.buyer != changed_by:
        recipients.add(order.buyer)
    if order.vendor.user != changed_by:
        recipients.add(order.vendor.user)
    
    for user in recipients:
        create_notification(
            recipient=user,
            notification_type=Notification.Type.ORDER_STATUS_CHANGED,
            title=f'Order {order.order_number} - {new_status}',
            message=f'Order {order.order_number} status changed to {new_status}',
            related_id=order.order_number,
        )