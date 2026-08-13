"""Management command to seed demo data."""

from django.core.management.base import BaseCommand

from seeders import accounts, catalog, invoices, orders, vendors

SEEDERS = {
    'accounts': accounts.seed,
    'vendors': vendors.seed,
    'catalog': catalog.seed,
    'orders': orders.seed,
    'invoices': invoices.seed,
}

SEED_ORDER = ['accounts', 'vendors', 'catalog', 'orders', 'invoices']


class Command(BaseCommand):
    help = 'Seed database with demo data'
    
    def add_arguments(self, parser):
        parser.add_argument('--app', type=str, help='Seed only a specific app')
    
    def handle(self, *args, **options):
        app = options['app']
        if app:
            self.stdout.write(self.style.SUCCESS(SEEDERS[app]()))
            return
        for name in SEED_ORDER:
            self.stdout.write(self.style.SUCCESS(SEEDERS[name]()))