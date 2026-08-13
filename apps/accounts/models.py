"""
Custom User model for the application.

Uses email as username instead of default username field.
Extends AbstractUser to maintain Django's authentication system.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model with email as primary identifier.
    
    Fields:
        email: User's email address (unique, used for login)
        username: Kept for Django admin compatibility (optional)
        first_name: User's first name
        last_name: User's last name
        is_active: Whether user account is active
        date_joined: When user registered
    
    Future Sprint 2 additions:
        - role field (admin, vendor, buyer, finance)
        - email_verified flag
        - phone number
    """
    
    # Make email required and unique
    email = models.EmailField(
        'email address',
        unique=True,
        help_text='Required. Valid email address.'
    )
    
    # Keep username optional (for Django admin compatibility)
    username = models.CharField(
        'username',
        max_length=150,
        blank=True,
        null=True,
        unique=True
    )
    
    # Use email for authentication instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email already required via USERNAME_FIELD
    
    class Meta:
        """Meta options for User model."""
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        """Return string representation of user."""
        return self.email or self.username or f'User {self.pk}'