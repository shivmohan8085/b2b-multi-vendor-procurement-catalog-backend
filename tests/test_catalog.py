"""Catalog API tests."""

import pytest

pytestmark = pytest.mark.django_db


def test_product_list_public(api_client, product):
    response = api_client.get('/api/v1/catalog/products/')
    assert response.status_code == 200
    assert response.data['count'] == 1


def test_product_create_requires_approved_vendor(auth_client, buyer_user, category):
    response = auth_client(buyer_user).post('/api/v1/catalog/products/create/', {
        'category': category.id, 'name': 'Keyboard', 'slug': 'kb-001',
        'sku': 'KB-001', 'description': 'Test', 'short_description': 'Test',
        'price': '999.00', 'stock_quantity': 10, 'status': 'active'
    }, format='json')
    assert response.status_code == 403


def test_product_create_vendor_success(auth_client, vendor_user, category):
    response = auth_client(vendor_user).post('/api/v1/catalog/products/create/', {
        'category': category.id, 'name': 'Keyboard', 'slug': 'kb-001',
        'sku': 'KB-001', 'description': 'Test', 'short_description': 'Test',
        'price': '999.00', 'stock_quantity': 10, 'status': 'active'
    }, format='json')
    assert response.status_code == 201


def test_product_update_other_vendor_forbidden(auth_client, vendor2_user, product):
    response = auth_client(vendor2_user).put(
        f'/api/v1/catalog/products/{product.slug}/update/',
        {'price': '1.00'}, format='json'
    )
    assert response.status_code == 403


def test_product_update_owner_success(auth_client, vendor_user, product):
    response = auth_client(vendor_user).put(
        f'/api/v1/catalog/products/{product.slug}/update/',
        {'price': '649.00'}, format='json'
    )
    assert response.status_code == 200