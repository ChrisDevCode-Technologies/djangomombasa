from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events_and_activities', '0005_event_rsvp_capacity_event_rsvp_deadline_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='end_date',
            field=models.DateTimeField(blank=True, help_text='When the event finishes. Leave blank for a single-day event ending on the start date.', null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='cfp_deadline',
            field=models.DateTimeField(blank=True, help_text='Latest moment speakers can submit proposals. Leave blank for no cutoff.', null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='cfv_deadline',
            field=models.DateTimeField(blank=True, help_text='Latest moment volunteers can sign up. Leave blank for no cutoff.', null=True),
        ),
    ]
