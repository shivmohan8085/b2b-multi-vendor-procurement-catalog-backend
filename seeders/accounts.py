"""Seed demo users."""

from apps.accounts.models import User

DEFAULT_PASSWORD = 'Password@123'

USERS = [
    {'email': 'admin@procureflow.com', 'role': 'admin', 'first_name': 'System', 'last_name': 'Admin', 'is_staff': True, 'is_superuser': True},
    {'email': 'buyer1@example.com', 'role': 'buyer', 'first_name': 'Rahul', 'last_name': 'Sharma'},
    {'email': 'buyer2@example.com', 'role': 'buyer', 'first_name': 'Priya', 'last_name': 'Patel'},
    {'email': 'vendor1@example.com', 'role': 'vendor', 'first_name': 'Amit', 'last_name': 'Verma'},
    {'email': 'vendor2@example.com', 'role': 'vendor', 'first_name': 'Sneha', 'last_name': 'Iyer'},
    {'email': 'finance@procureflow.com', 'role': 'finance', 'first_name': 'Karan', 'last_name': 'Mehta'},
]


def seed():
    for data in USERS:
        if not User.objects.filter(email=data['email']).exists():
            User.objects.create_user(
                email=data['email'],
                password=DEFAULT_PASSWORD,
                role=data['role'],
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                is_staff=data.get('is_staff', False),
                is_superuser=data.get('is_superuser', False),
            )
    return f'{len(USERS)} users seeded'