"""
Catalog app configuration.
"""

from django.apps import AppConfig


class CatalogConfig(AppConfig):
    """Configuration for the catalog app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.catalog'
    verbose_name = 'Catalog'
    
    def ready(self):
        """Import signals when app is ready."""
        import apps.catalog.signals  # noqa: F401