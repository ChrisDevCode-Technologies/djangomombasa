from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app', '0009_remove_member_models'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='Tag',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(max_length=50, unique=True)),
                    ],
                    options={
                        'db_table': 'app_tag',
                    },
                ),
                migrations.CreateModel(
                    name='Event',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(max_length=200)),
                        ('slug', models.SlugField(blank=True, max_length=220, unique=True)),
                        ('date', models.DateTimeField()),
                        ('rsvp_link', models.URLField(blank=True)),
                        ('details', models.TextField()),
                        ('tags', models.ManyToManyField(blank=True, related_name='events', to='events_and_activities.tag')),
                    ],
                    options={
                        'db_table': 'app_event',
                        'ordering': ['date'],
                    },
                ),
            ],
            database_operations=[],
        ),
    ]
