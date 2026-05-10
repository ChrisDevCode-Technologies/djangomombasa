from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_remove_member_models'),
        ('events_and_activities', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterField(
                    model_name='partner',
                    name='events',
                    field=models.ManyToManyField(blank=True, related_name='partners', to='events_and_activities.event'),
                ),
                migrations.AlterField(
                    model_name='sponsor',
                    name='events',
                    field=models.ManyToManyField(blank=True, related_name='sponsors', to='events_and_activities.event'),
                ),
                migrations.DeleteModel(name='Event'),
                migrations.DeleteModel(name='Tag'),
            ],
            database_operations=[],
        ),
    ]
