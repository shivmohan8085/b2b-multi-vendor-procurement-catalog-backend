"""Serializers for order management."""

from rest_framework import serializers
from apps.orders.models import Address, Order, OrderItem, OrderStatusHistory


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'label', 'address_type', 'company_name', 'contact_person', 'phone', 'address_line1', 'address_line2', 'city', 'state', 'pincode', 'is_default']
        read_only_fields = ['id']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_sku', 'unit_price', 'quantity', 'delivered_quantity', 'line_total']
        read_only_fields = ['id', 'product_name', 'product_sku', 'unit_price', 'line_total']


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_email = serializers.EmailField(source='changed_by.email', read_only=True)
    
    class Meta:
        model = OrderStatusHistory
        fields = ['id', 'from_status', 'to_status', 'changed_by_email', 'remarks', 'created_at']


class OrderListSerializer(serializers.ModelSerializer):
    buyer_email = serializers.EmailField(source='buyer.email', read_only=True)
    vendor_name = serializers.CharField(source='vendor.company_name', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'buyer_email', 'vendor_name', 'status', 'total_amount', 'created_at']


class OrderDetailSerializer(serializers.ModelSerializer):
    buyer_email = serializers.EmailField(source='buyer.email', read_only=True)
    vendor_name = serializers.CharField(source='vendor.company_name', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    shipping = AddressSerializer(source='shipping_address', read_only=True)
    billing = AddressSerializer(source='billing_address', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'buyer_email', 'vendor_name', 'status', 'shipping', 'billing', 'items', 'subtotal', 'tax_amount', 'discount_amount', 'shipping_charge', 'total_amount', 'notes', 'status_history', 'created_at', 'updated_at']


class OrderItemCreateSerializer(serializers.Serializer):
    product = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    vendor = serializers.IntegerField()
    shipping_address = serializers.IntegerField()
    billing_address = serializers.IntegerField()
    items = OrderItemCreateSerializer(many=True)
    notes = serializers.CharField(required=False, allow_blank=True, default='')