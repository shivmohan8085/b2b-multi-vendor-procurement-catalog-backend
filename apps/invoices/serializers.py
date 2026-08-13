"""Serializers for invoice management."""

from rest_framework import serializers
from apps.invoices.models import Invoice, InvoiceItem, Payment


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ['id', 'product_name', 'product_sku', 'unit_price', 'quantity', 'line_total']


class PaymentSerializer(serializers.ModelSerializer):
    recorded_by_email = serializers.EmailField(source='recorded_by.email', read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'method', 'reference_number', 'recorded_by_email', 'paid_at']


class InvoiceListSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    vendor_name = serializers.CharField(source='vendor.company_name', read_only=True)
    buyer_email = serializers.EmailField(source='buyer.email', read_only=True)
    
    class Meta:
        model = Invoice
        fields = ['id', 'invoice_number', 'order_number', 'vendor_name', 'buyer_email', 'issue_date', 'due_date', 'total_amount', 'status', 'created_at']


class InvoiceDetailSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    vendor_name = serializers.CharField(source='vendor.company_name', read_only=True)
    buyer_email = serializers.EmailField(source='buyer.email', read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Invoice
        fields = ['id', 'invoice_number', 'order_number', 'vendor_name', 'buyer_email', 'issue_date', 'due_date', 'subtotal', 'tax_amount', 'total_amount', 'status', 'pdf_file', 'items', 'payments', 'created_at', 'updated_at']


class InvoiceCreateSerializer(serializers.Serializer):
    order_number = serializers.CharField()


class PaymentRecordSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    method = serializers.ChoiceField(choices=Payment.Method.choices)
    reference_number = serializers.CharField(required=False, allow_blank=True, default='')