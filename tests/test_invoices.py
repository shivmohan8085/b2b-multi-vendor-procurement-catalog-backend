"""Invoice API tests."""

import pytest

pytestmark = pytest.mark.django_db


def test_invoice_requires_delivered_order(auth_client, buyer_user, vendor_user, product, address):
    order = auth_client(buyer_user).post('/api/v1/orders/create/', {
        'vendor': vendor_user.vendor_profile.id,
        'shipping_address': address.id,
        'billing_address': address.id,
        'items': [{'product': product.id, 'quantity': 2}],
    }, format='json').data
    
    response = auth_client(vendor_user).post(
        '/api/v1/invoices/create/',
        {'order_number': order['order_number']}, format='json'
    )
    assert response.status_code == 400