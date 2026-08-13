"""URL configuration for orders app."""

from django.urls import path
from apps.orders.views import (
    AddressListCreateView, OrderCreateView, OrderListView,
    OrderDetailView, OrderApprovalView, OrderStatusUpdateView,
    OrderHistoryView
)

app_name = 'orders'

urlpatterns = [
    path('addresses/', AddressListCreateView.as_view(), name='address-list-create'),
    path('create/', OrderCreateView.as_view(), name='order-create'),
    path('', OrderListView.as_view(), name='order-list'),
    path('<str:order_number>/', OrderDetailView.as_view(), name='order-detail'),
    path('<str:order_number>/approve/', OrderApprovalView.as_view(), name='order-approval'),
    path('<str:order_number>/status/', OrderStatusUpdateView.as_view(), name='order-status'),
    path('<str:order_number>/history/', OrderHistoryView.as_view(), name='order-history'),
]