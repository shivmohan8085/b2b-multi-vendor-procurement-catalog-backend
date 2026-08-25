"""Order API tests."""

import pytest

pytestmark = pytest.mark.django_db


def create_order_payload(vendor_id, address_id, product_id):
    return {
        'vendor': vendor_id,
        'shipping_address': address_id,
        'billing_address': address_id,
        'items': [{'product': product_id, 'quantity': 5}],
    }


def test_order_create_success(auth_client, buyer_user, vendor_user, product, address):
    response = auth_client(buyer_user).post(
        '/api/v1/orders/create/',
        create_order_payload(vendor_user.vendor_profile.id, address.id, product.id),
        format='json'
    )
    assert response.status_code == 201
    assert response.data['status'] == 'pending_approval'


def test_order_buyer_cannot_approve(auth_client, buyer_user, vendor_user, product, address):
    order = auth_client(buyer_user).post(
        '/api/v1/orders/create/',
        create_order_payload(vendor_user.vendor_profile.id, address.id, product.id),
        format='json'
    ).data
    response = auth_client(buyer_user).post(
        f"/api/v1/orders/{order['order_number']}/status/",
        {'status': 'approved'}, format='json'
    )
    assert response.status_code == 400


def test_invalid_transition_rejected(auth_client, admin_user, buyer_user, vendor_user, product, address):
    order = auth_client(buyer_user).post(
        '/api/v1/orders/create/',
        create_order_payload(vendor_user.vendor_profile.id, address.id, product.id),
        format='json'
    ).data
    # pending_approval se seedha delivered - invalid transition
    response = auth_client(admin_user).post(
        f"/api/v1/orders/{order['order_number']}/status/",
        {'status': 'delivered'}, format='json'
    )
    assert response.status_code == 400


def test_admin_approve_reserves_stock(auth_client, admin_user, buyer_user, vendor_user, product, address):
    order = auth_client(buyer_user).post(
        '/api/v1/orders/create/',
        create_order_payload(vendor_user.vendor_profile.id, address.id, product.id),
        format='json'
    ).data
    response = auth_client(admin_user).post(
        f"/api/v1/orders/{order['order_number']}/approve/",
        {'action': 'approve'}, format='json'
    )
    assert response.status_code == 200
    product.refresh_from_db()
    assert product.stock_quantity == 95