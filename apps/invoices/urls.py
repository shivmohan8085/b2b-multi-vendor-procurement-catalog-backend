"""URL configuration for invoices app."""

from django.urls import path
from apps.invoices.views import (
    InvoiceCreateView, InvoiceListView, InvoiceDetailView,
    InvoicePDFView, PaymentRecordView
)

app_name = 'invoices'

urlpatterns = [
    path('create/', InvoiceCreateView.as_view(), name='invoice-create'),
    path('', InvoiceListView.as_view(), name='invoice-list'),
    path('<str:invoice_number>/', InvoiceDetailView.as_view(), name='invoice-detail'),
    path('<str:invoice_number>/pdf/', InvoicePDFView.as_view(), name='invoice-pdf'),
    path('<str:invoice_number>/payments/', PaymentRecordView.as_view(), name='invoice-payments'),
]