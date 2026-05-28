from urllib.parse import urljoin

from django.conf import settings
from django.templatetags.static import static

from .models import SocialLink


def social_links(request):
    return {'social_links': SocialLink.objects.all()}


def site_metadata(request):
    site_url = settings.SITE_URL.rstrip('/')
    default_image = urljoin(f'{site_url}/', static('images/logo.jpg'))
    return {
        'site_name': settings.SITE_NAME,
        'site_url': site_url,
        'default_meta_description': (
            'Django Mombasa is a coastal Kenya developer community for learning Django, '
            'Python, web development, and building practical software together.'
        ),
        'default_og_image': default_image,
    }
