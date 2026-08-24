"""Views for vendor management."""

from django.core.cache import cache
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import Product
from apps.orders.models import Order
from apps.vendors.models import VendorProfile, VendorKYCDocument, VendorApprovalLog
from apps.vendors.serializers import (
    VendorProfileSerializer, VendorProfileCreateSerializer,
    VendorKYCDocumentSerializer, VendorApprovalLogSerializer,
    VendorApprovalSerializer, VendorListSerializer
)
from apps.vendors.permissions import IsVendorOwner, IsAdminUser


class VendorRegisterView(APIView):
    """Register as a vendor."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if hasattr(request.user, 'vendor_profile'):
            return Response({'error': 'Vendor profile already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = VendorProfileCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        vendor = serializer.save(user=request.user)
        
        request.user.role = 'vendor'
        request.user.save()
        
        VendorApprovalLog.objects.create(
            vendor=vendor,
            action='submitted',
            performed_by=request.user,
            remarks='Vendor profile submitted for approval'
        )
        
        return Response(VendorProfileSerializer(vendor).data, status=status.HTTP_201_CREATED)


class VendorProfileView(APIView):
    """Get or update vendor profile."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        vendor = get_object_or_404(VendorProfile, user=request.user)
        serializer = VendorProfileSerializer(vendor)
        return Response(serializer.data)
    
    def put(self, request):
        vendor = get_object_or_404(VendorProfile, user=request.user)
        
        if vendor.approval_status == 'approved':
            return Response({'error': 'Cannot edit approved vendor profile'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = VendorProfileSerializer(vendor, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class VendorListView(APIView):
    """List all vendors (admin only)."""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        vendors = VendorProfile.objects.select_related('user').all()
        serializer = VendorListSerializer(vendors, many=True)
        return Response(serializer.data)


class VendorDetailView(APIView):
    """Get vendor details by ID (admin only)."""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request, vendor_id):
        vendor = get_object_or_404(VendorProfile, id=vendor_id)
        serializer = VendorProfileSerializer(vendor)
        return Response(serializer.data)


class VendorApprovalView(APIView):
    """Approve or reject vendor (admin only)."""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def post(self, request, vendor_id):
        vendor = get_object_or_404(VendorProfile, id=vendor_id)
        serializer = VendorApprovalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        action = serializer.validated_data['action']
        remarks = serializer.validated_data.get('remarks', '')
        
        if action == 'approve':
            vendor.approval_status = 'approved'
            vendor.approved_by = request.user
            vendor.approved_at = timezone.now()
            vendor.rejection_reason = ''
            log_action = 'approved'
        else:
            vendor.approval_status = 'rejected'
            vendor.rejection_reason = remarks
            log_action = 'rejected'
        
        vendor.save()
        
        VendorApprovalLog.objects.create(
            vendor=vendor,
            action=log_action,
            performed_by=request.user,
            remarks=remarks
        )
        
        return Response(VendorProfileSerializer(vendor).data)


class VendorKYCDocumentView(APIView):
    """Upload KYC documents."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        vendor = get_object_or_404(VendorProfile, user=request.user)
        
        serializer = VendorKYCDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        document = serializer.save(
            vendor=vendor,
            original_filename=request.FILES['document'].name
        )
        
        return Response(VendorKYCDocumentSerializer(document).data, status=status.HTTP_201_CREATED)
    
    def get(self, request):
        vendor = get_object_or_404(VendorProfile, user=request.user)
        documents = VendorKYCDocument.objects.filter(vendor=vendor)
        serializer = VendorKYCDocumentSerializer(documents, many=True)
        return Response(serializer.data)


class VendorApprovalLogView(APIView):
    """Get approval logs for a vendor (admin only)."""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request, vendor_id):
        vendor = get_object_or_404(VendorProfile, id=vendor_id)
        logs = VendorApprovalLog.objects.filter(vendor=vendor)
        serializer = VendorApprovalLogSerializer(logs, many=True)
        return Response(serializer.data)


class VendorDashboardView(APIView):
    """Vendor dashboard stats with Redis caching."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not hasattr(request.user, 'vendor_profile'):
            return Response({'error': 'Vendor profile not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        vendor = request.user.vendor_profile
        cache_key = f'vendor_dashboard_{vendor.id}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        stats = {
            'total_products': Product.objects.filter(vendor=vendor).count(),
            'active_products': Product.objects.filter(vendor=vendor, status='active').count(),
            'low_stock_products': Product.objects.filter(vendor=vendor, stock_quantity__lte=F('low_stock_threshold')).count(),
            'total_orders': Order.objects.filter(vendor=vendor).count(),
            'pending_orders': Order.objects.filter(vendor=vendor, status='pending_approval').count(),
            'total_revenue': Order.objects.filter(vendor=vendor, status__in=['delivered', 'invoiced', 'completed']).aggregate(total=Sum('total_amount'))['total'] or 0,
        }
        
        cache.set(cache_key, stats, timeout=300)
        
        return Response(stats)