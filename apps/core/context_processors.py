"""KekiCakes – Core context processors"""
from django.conf import settings


def site_context(request):
    """Inject site-wide variables into every template context."""
    return {
        'WHATSAPP_NUMBER': getattr(settings, 'WHATSAPP_NUMBER', '254712345678'),
        'SITE_NAME': 'Keki Cakes',
        'SITE_TAGLINE': 'Baked with Love, Delivered with Joy',
    }
