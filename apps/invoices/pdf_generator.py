"""Invoice PDF generation using xhtml2pdf."""

from io import BytesIO
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from xhtml2pdf import pisa


def render_invoice_html(invoice):
    return render_to_string('pdf/invoice/invoice_pdf.html', {'invoice': invoice})


def generate_invoice_pdf(invoice):
    html = render_invoice_html(invoice)
    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(src=html, dest=buffer)
    if pisa_status.err:
        raise ValueError('PDF generation failed')
    invoice.pdf_file.save(f'{invoice.invoice_number}.pdf', ContentFile(buffer.getvalue()), save=True)
    return invoice