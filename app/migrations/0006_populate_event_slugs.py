from django.db import migrations
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    Event = apps.get_model('app', 'Event')
    for event in Event.objects.filter(slug=''):
        base = slugify(event.name)
        slug = base
        n = 1
        while Event.objects.filter(slug=slug).exclude(pk=event.pk).exists():
            slug = f'{base}-{n}'
            n += 1
        event.slug = slug
        event.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_add_event_slug'),
    ]

    operations = [
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
    ]
