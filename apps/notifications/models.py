"""Notification model for user alerts."""

from django.db import models
from django.conf import settings


class Notification(models.Model):
    class Type(models.TextChoices):
        ORDER_CREATED = 'order_created', 'Order Created'
        ORDER_STATUS_CHANGED = 'order_status_changed', 'Order Status Changed'
        VENDOR_APPROVED = 'vendor_approved', 'Vendor Approved'
        VENDOR_REJECTED = 'vendor_rejected', 'Vendor Rejected'
        INVOICE_CREATED = 'invoice_created', 'Invoice Created'
        PAYMENT_RECEIVED = 'payment_received', 'Payment Received'
        LOW_STOCK = 'low_stock', 'Low Stock Alert'
        SYSTEM = 'system', 'System'
    
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=Type.choices)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    related_id = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
        ]
    
    def __str__(self):
        return f'{self.notification_type} for {self.recipient.email}'