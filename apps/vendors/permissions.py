"""Custom permissions for vendor management."""

from rest_framework.permissions import BasePermission


class IsVendorOwner(BasePermission):
    """Allow vendor to access only their own profile."""
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsAdminUser(BasePermission):
    """Allow only admin users to perform action."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_staff or request.user.role == 'admin'


class IsApprovedVendor(BasePermission):
    """Allow only approved vendors to access."""
    
    def has_permission(self, request, view):
        if not hasattr(request.user, 'vendor_profile'):
            return False
        return request.user.vendor_profile.approval_status == 'approved'