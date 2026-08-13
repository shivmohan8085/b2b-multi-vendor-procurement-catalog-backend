"""Custom User model with email authentication and role-based access."""

from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.accounts.managers import UserManager


class User(AbstractUser):
    """Custom user model with email as primary identifier."""
    
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        VENDOR = 'vendor', 'Vendor'
        BUYER = 'buyer', 'Buyer'
        FINANCE = 'finance', 'Finance'
    
    email = models.EmailField('email address', unique=True)
    username = models.CharField('username', max_length=150, blank=True, null=True, unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.BUYER)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.email