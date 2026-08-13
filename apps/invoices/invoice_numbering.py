"""Invoice number generation."""

import random
import string
from django.utils import timezone
from apps.invoices.models import Invoice


def generate_invoice_number():
    while True:
        number = f"INV-{timezone.now().year}-{''.join(random.choices(string.digits, k=5))}"
        if not Invoice.objects.filter(invoice_number=number).exists():
            return number