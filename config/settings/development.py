"""
Development settings for b2b-multi-vendor-procurement-catalog-backend project.

These settings are used only during local development.
Database and other sensitive values are loaded from the .env file via base.py.
"""

from .base import *  # noqa: F401, F403

# Enable debug mode in development
DEBUG = True

# Allowed hosts for local development
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# CORS: allow all origins in development for easy testing
CORS_ALLOW_ALL_ORIGINS = True

# Simplified password validation for faster development
AUTH_PASSWORD_VALIDATORS = []

# Django Debug Toolbar
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
INTERNAL_IPS = ['127.0.0.1']
