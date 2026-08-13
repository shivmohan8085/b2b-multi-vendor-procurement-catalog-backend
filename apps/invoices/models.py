"""Invoice models for B2B procurement system."""

from django.db import models
from django.conf import settings


class Invoice(models.Model):
    """Invoice generated against a delivered order."""
    
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        ISSUED = 'issued', 'Issued'
        PAID = 'paid', 'Paid'
        OVERDUE = 'overdue', 'Overdue'
        CANCELLED = 'cancelled', 'Cancelled'
    
    invoice_number = models.CharField(max_length=20, unique=True, editable=False)
    order = models.OneToOneField('orders.Order', on_delete=models.PROTECT, related_name='invoice')
    vendor = models.ForeignKey('vendors.VendorProfile', on_delete=models.PROTECT, related_name='invoices')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='invoices')
    
    issue_date = models.DateField()
    due_date = models.DateField()
    
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ISSUED)
    pdf_file = models.FileField(upload_to='private/invoices/%Y/%m/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['vendor', 'status']),
            models.Index(fields=['buyer', 'status']),
        ]
    
    def __str__(self):
        return self.invoice_number


class InvoiceItem(models.Model):
    """Line item of an invoice."""
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=255)
    product_sku = models.CharField(max_length=50)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    line_total = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        verbose_name = 'Invoice Item'
        verbose_name_plural = 'Invoice Items'
        ordering = ['id']
    
    def __str__(self):
        return f'{self.invoice.invoice_number} - {self.product_name}'


class Payment(models.Model):
    """Payment recorded against an invoice."""
    
    class Method(models.TextChoices):
        BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'
        UPI = 'upi', 'UPI'
        CHEQUE = 'cheque', 'Cheque'
        CARD = 'card', 'Card'
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=Method.choices)
    reference_number = models.CharField(max_length=100, blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    paid_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-paid_at']
    
    def __str__(self):
        return f'{self.invoice.invoice_number} - {self.amount}'