# Generated manually for race-safe member ID generation

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_page'),
    ]

    operations = [
        migrations.CreateModel(
            name='MemberIdSequence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('next_number', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Member ID Sequence',
                'verbose_name_plural': 'Member ID Sequence',
            },
        ),
    ]
