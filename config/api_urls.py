"""API URL configuration."""

from django.urls import path, include
from apps.core.health_views import health_check

urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('v1/auth/', include('apps.accounts.urls')),
]