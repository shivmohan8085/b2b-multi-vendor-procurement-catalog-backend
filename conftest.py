"""Shared pytest fixtures."""

import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.catalog.models import Category, Product
from apps.orders.models import Address
from apps.vendors.models import VendorProfile


@pytest.fixture(autouse=True)
def test_settings(settings):
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client):
    def _auth(user):
        api_client.force_authenticate(user=user)
        return api_client
    return _auth


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        email='admin@test.com', password='Test@12345',
        role='admin', is_staff=True, is_superuser=True
    )


@pytest.fixture
def buyer_user(db):
    return User.objects.create_user(email='buyer@test.com', password='Test@12345', role='buyer')


@pytest.fixture
def vendor_user(db):
    user = User.objects.create_user(email='vendor@test.com', password='Test@12345', role='vendor')
    VendorProfile.objects.create(
        user=user, company_name='Test Vendor', gst_number='07AAACA1234A1Z5',
        pan_number='AAACA1234A', phone='+919999999999', email='vendor@test.com',
        approval_status='approved'
    )
    return user


@pytest.fixture
def vendor2_user(db):
    user = User.objects.create_user(email='vendor2@test.com', password='Test@12345', role='vendor')
    VendorProfile.objects.create(
        user=user, company_name='Other Vendor', gst_number='27BBBGB9876B2Z4',
        pan_number='BBBGB9876B', phone='+918888888888', email='vendor2@test.com',
        approval_status='approved'
    )
    return user


@pytest.fixture
def category(db):
    return Category.objects.create(name='Electronics', slug='electronics')


@pytest.fixture
def product(vendor_user, category):
    return Product.objects.create(
        vendor=vendor_user.vendor_profile, category=category,
        name='Mouse', slug='mouse-001', sku='M-001',
        price='599.00', stock_quantity=100, status='active'
    )


@pytest.fixture
def address(buyer_user):
    return Address.objects.create(
        user=buyer_user, contact_person='Test Buyer', phone='+911111111111',
        address_line1='123 Test Street', city='Mumbai', state='Maharashtra', pincode='400001'
    )