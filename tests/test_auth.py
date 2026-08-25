"""Auth API tests."""

import pytest

pytestmark = pytest.mark.django_db


def test_register_user(api_client):
    response = api_client.post('/api/v1/auth/register/', {
        'email': 'new@test.com',
        'password': 'Test@12345',
        'password_confirm': 'Test@12345',  # ← password2 ki jagah password_confirm
        'first_name': 'New',
        'last_name': 'User',
        'phone': '+911234567890'  # ← Add karo (optional ho to bhi bhej do)
    }, format='json')
    assert response.status_code == 201


def test_login_success(api_client, buyer_user):
    response = api_client.post('/api/v1/auth/login/', {
        'email': 'buyer@test.com', 'password': 'Test@12345'
    }, format='json')
    assert response.status_code == 200
    if 'data' in response.data:
        assert 'access' in response.data['data']
    else:
        assert 'access' in response.data


def test_login_wrong_password(api_client, buyer_user):
    response = api_client.post('/api/v1/auth/login/', {
        'email': 'buyer@test.com', 'password': 'wrongpass'
    }, format='json')
    assert response.status_code == 401