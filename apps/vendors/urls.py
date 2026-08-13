"""URL configuration for vendors app."""

from django.urls import path
from apps.vendors.views import (
    VendorRegisterView, VendorProfileView, VendorListView,
    VendorDetailView, VendorApprovalView, VendorKYCDocumentView,
    VendorApprovalLogView
)

app_name = 'vendors'

urlpatterns = [
    path('register/', VendorRegisterView.as_view(), name='vendor-register'),
    path('profile/', VendorProfileView.as_view(), name='vendor-profile'),
    path('list/', VendorListView.as_view(), name='vendor-list'),
    path('<int:vendor_id>/', VendorDetailView.as_view(), name='vendor-detail'),
    path('<int:vendor_id>/approve/', VendorApprovalView.as_view(), name='vendor-approval'),
    path('<int:vendor_id>/logs/', VendorApprovalLogView.as_view(), name='vendor-logs'),
    path('kyc/', VendorKYCDocumentView.as_view(), name='vendor-kyc'),
]