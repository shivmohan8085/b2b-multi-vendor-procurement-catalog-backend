"""Serializers for vendor management."""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.vendors.models import VendorProfile, VendorKYCDocument, VendorApprovalLog

User = get_user_model()


class VendorProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = VendorProfile
        fields = ['id', 'user', 'user_email', 'company_name', 'gst_number', 'pan_number', 'contact_person', 'phone', 'email', 'address', 'city', 'state', 'pincode', 'website', 'logo', 'approval_status', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'approval_status', 'created_at', 'updated_at']


class VendorProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProfile
        fields = ['company_name', 'gst_number', 'pan_number', 'contact_person', 'phone', 'email', 'address', 'city', 'state', 'pincode', 'website', 'logo']


class VendorKYCDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorKYCDocument
        fields = ['id', 'vendor', 'document_type', 'document', 'original_filename', 'verification_status', 'uploaded_at']
        read_only_fields = ['id', 'vendor', 'verification_status', 'uploaded_at']


class VendorApprovalLogSerializer(serializers.ModelSerializer):
    performed_by_email = serializers.EmailField(source='performed_by.email', read_only=True)
    
    class Meta:
        model = VendorApprovalLog
        fields = ['id', 'vendor', 'action', 'performed_by', 'performed_by_email', 'remarks', 'created_at']
        read_only_fields = ['id', 'vendor', 'performed_by', 'created_at']


class VendorApprovalSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    remarks = serializers.CharField(required=False, allow_blank=True, default='')


class VendorListSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = VendorProfile
        fields = ['id', 'company_name', 'user_email', 'city', 'state', 'approval_status', 'is_active', 'created_at']