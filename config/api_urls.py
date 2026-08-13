"""
API URL configuration.

All API endpoints will be registered here with versioning.
"""

from django.urls import path, include
from apps.core.health_views import health_check

urlpatterns = [
    # Health check endpoint
    path('health/', health_check, name='health-check'),
    
    # API v1 endpoints (will be added in future sprints)
    # path('v1/auth/', include('apps.accounts.urls')),
    # path('v1/vendors/', include('apps.vendors.urls')),
    # path('v1/catalog/', include('apps.catalog.urls')),
    # path('v1/orders/', include('apps.orders.urls')),
    # path('v1/invoices/', include('apps.invoices.urls')),
    # path('v1/notifications/', include('apps.notifications.urls')),
    # path('v1/dashboard/', include('apps.dashboard.urls')),
]