"""Views for invoice management."""

from django.core.exceptions import ValidationError
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.invoices import services
from apps.invoices.models import Invoice
from apps.invoices.pdf_generator import generate_invoice_pdf
from apps.invoices.serializers import (
    InvoiceCreateSerializer, InvoiceDetailSerializer,
    InvoiceListSerializer, PaymentRecordSerializer
)
from apps.orders.models import Order


class InvoiceCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = InvoiceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = get_object_or_404(Order, order_number=serializer.validated_data['order_number'])
        
        user = request.user
        is_vendor_owner = hasattr(user, 'vendor_profile') and order.vendor == user.vendor_profile
        if not (user.role == 'admin' or user.is_staff or user.role == 'finance' or is_vendor_owner):
            return Response({'error': 'Not allowed'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            invoice = services.create_invoice_from_order(order, user)
        except ValidationError as e:
            return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)
        return Response(InvoiceDetailSerializer(invoice).data, status=status.HTTP_201_CREATED)


class InvoiceListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        queryset = Invoice.objects.select_related('order', 'vendor', 'buyer')
        if not (user.role == 'admin' or user.is_staff or user.role == 'finance'):
            if hasattr(user, 'vendor_profile'):
                queryset = queryset.filter(vendor=user.vendor_profile)
            else:
                queryset = queryset.filter(buyer=user)
        
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return Response(InvoiceListSerializer(queryset, many=True).data)


class InvoiceDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, invoice_number):
        invoice = get_object_or_404(
            Invoice.objects.select_related('order', 'vendor', 'buyer').prefetch_related('items', 'payments'),
            invoice_number=invoice_number
        )
        if not user_can_access(request.user, invoice):
            return Response({'error': 'Not allowed'}, status=status.HTTP_403_FORBIDDEN)
        return Response(InvoiceDetailSerializer(invoice).data)


class InvoicePDFView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, invoice_number):
        invoice = get_object_or_404(Invoice, invoice_number=invoice_number)
        if not user_can_access(request.user, invoice):
            return Response({'error': 'Not allowed'}, status=status.HTTP_403_FORBIDDEN)
        
        if not invoice.pdf_file:
            generate_invoice_pdf(invoice)
        
        return FileResponse(
            invoice.pdf_file.open('rb'),
            as_attachment=True,
            filename=f'{invoice.invoice_number}.pdf',
            content_type='application/pdf'
        )


class PaymentRecordView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, invoice_number):
        invoice = get_object_or_404(Invoice, invoice_number=invoice_number)
        user = request.user
        if not (user.role == 'admin' or user.is_staff or user.role == 'finance' or invoice.buyer == user):
            return Response({'error': 'Not allowed'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = PaymentRecordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.record_payment(
            invoice, user,
            amount=serializer.validated_data['amount'],
            method=serializer.validated_data['method'],
            reference_number=serializer.validated_data.get('reference_number', ''),
        )
        return Response(InvoiceDetailSerializer(invoice).data, status=status.HTTP_201_CREATED)


def user_can_access(user, invoice):
    return (
        user.role == 'admin' or user.is_staff or user.role == 'finance'
        or invoice.buyer == user
        or (hasattr(user, 'vendor_profile') and invoice.vendor == user.vendor_profile)
    )