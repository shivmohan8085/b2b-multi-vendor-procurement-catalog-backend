"""
Orders app configuration.
"""

from django.apps import AppConfig


class OrdersConfig(AppConfig):
    """Configuration for the orders app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.orders'
    verbose_name = 'Orders'
    
    def ready(self):
        """Import signals when app is ready."""
        import apps.orders.signals  # noqa: F401