import re

from django import template

register = template.Library()


@register.filter
def truncate_sentences(value, count=3):
    """Truncate text to a given number of sentences."""
    sentences = re.findall(r'[^.!?]*[.!?]', str(value))
    if len(sentences) <= count:
        return value
    return ''.join(sentences[:count]).strip()
