"""Vendor models for B2B procurement system."""

from django.db import models
from django.conf import settings


class VendorProfile(models.Model):
    """Vendor company profile linked to a user account."""
    
    class ApprovalStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendor_profile')
    company_name = models.CharField(max_length=255)
    gst_number = models.CharField(max_length=15, unique=True)
    pan_number = models.CharField(max_length=10, unique=True)
    contact_person = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=6, blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='media/public/vendor_logos/', blank=True, null=True)
    approval_status = models.CharField(max_length=20, choices=ApprovalStatus.choices, default=ApprovalStatus.PENDING)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_vendors')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Vendor Profile'
        verbose_name_plural = 'Vendor Profiles'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.company_name


class VendorKYCDocument(models.Model):
    """KYC documents uploaded by vendor."""
    
    class DocumentType(models.TextChoices):
        GST_CERTIFICATE = 'gst_certificate', 'GST Certificate'
        PAN_CARD = 'pan_card', 'PAN Card'
        ADDRESS_PROOF = 'address_proof', 'Address Proof'
        BANK_DETAILS = 'bank_details', 'Bank Details'
        OTHER = 'other', 'Other'
    
    class VerificationStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        VERIFIED = 'verified', 'Verified'
        REJECTED = 'rejected', 'Rejected'
    
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='kyc_documents')
    document_type = models.CharField(max_length=30, choices=DocumentType.choices)
    document = models.FileField(upload_to='media/private/vendor_documents/')
    original_filename = models.CharField(max_length=255)
    verification_status = models.CharField(max_length=20, choices=VerificationStatus.choices, default=VerificationStatus.PENDING)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Vendor KYC Document'
        verbose_name_plural = 'Vendor KYC Documents'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f'{self.vendor.company_name} - {self.document_type}'


class VendorApprovalLog(models.Model):
    """Log of vendor approval/rejection actions."""
    
    class Action(models.TextChoices):
        SUBMITTED = 'submitted', 'Submitted'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        RESUBMITTED = 'resubmitted', 'Resubmitted'
    
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='approval_logs')
    action = models.CharField(max_length=20, choices=Action.choices)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Vendor Approval Log'
        verbose_name_plural = 'Vendor Approval Logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.vendor.company_name} - {self.action}'