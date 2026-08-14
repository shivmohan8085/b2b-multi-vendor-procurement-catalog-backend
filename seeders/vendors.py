"""Seed demo vendor profiles."""

from django.utils import timezone
from apps.accounts.models import User
from apps.vendors.models import VendorProfile, VendorApprovalLog

VENDORS = [
    {'email': 'shivbhatt0113@gmail.com', 'company_name': 'Acme Suppliers', 'gst_number': '07AAACA1234A1Z5', 'pan_number': 'AAACA1234A', 'city': 'Mumbai', 'state': 'Maharashtra'},
]


def seed():
    admin = User.objects.filter(role='admin').first()
    for data in VENDORS:
        user = User.objects.get(email=data['email'])
        vendor, created = VendorProfile.objects.get_or_create(
            user=user,
            defaults={
                'company_name': data['company_name'],
                'gst_number': data['gst_number'],
                'pan_number': data['pan_number'],
                'city': data['city'],
                'state': data['state'],
                'phone': '+919876543210',
                'email': data['email'],
                'approval_status': 'approved',
                'approved_by': admin,
                'approved_at': timezone.now(),
            }
        )
        if created:
            VendorApprovalLog.objects.create(vendor=vendor, action='submitted', performed_by=user)
            VendorApprovalLog.objects.create(vendor=vendor, action='approved', performed_by=admin, remarks='KYC verified')
    return f'{len(VENDORS)} vendors seeded'