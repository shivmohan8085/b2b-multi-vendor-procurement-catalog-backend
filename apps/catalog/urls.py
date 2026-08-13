"""URL configuration for catalog app."""

from django.urls import path
from apps.catalog.views import (
    CategoryListView, TagListView, ProductListView,
    ProductDetailView, ProductCreateView, ProductUpdateView,
    ProductImageView
)

app_name = 'catalog'

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('tags/', TagListView.as_view(), name='tag-list'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/create/', ProductCreateView.as_view(), name='product-create'),
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/<slug:slug>/update/', ProductUpdateView.as_view(), name='product-update'),
    path('products/<slug:slug>/delete/', ProductUpdateView.as_view(), name='product-delete'),
    path('products/<slug:slug>/images/', ProductImageView.as_view(), name='product-images'),
]