from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events_and_activities', '0007_alter_event_details'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='location',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Where the event is held (venue name and/or address). Shown on the events listing.',
                max_length=255,
            ),
            preserve_default=False,
        ),
    ]
