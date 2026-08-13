"""Custom permissions for catalog management."""

from rest_framework.permissions import BasePermission


class IsProductOwner(BasePermission):
    """Allow vendor to edit/delete only their own products."""
    
    def has_object_permission(self, request, view, obj):
        return obj.vendor.user == request.user


class IsApprovedVendorPermission(BasePermission):
    """Allow only approved vendors to create products."""
    
    def has_permission(self, request, view):
        if not hasattr(request.user, 'vendor_profile'):
            return False
        return request.user.vendor_profile.approval_status == 'approved'