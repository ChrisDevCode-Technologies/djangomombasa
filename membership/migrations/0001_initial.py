from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app', '0008_member_receive_email_communications_and_more'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='MemberIdSequence',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('next_number', models.PositiveIntegerField(default=0)),
                    ],
                    options={
                        'verbose_name': 'Member ID Sequence',
                        'verbose_name_plural': 'Member ID Sequence',
                        'db_table': 'app_memberidsequence',
                    },
                ),
                migrations.CreateModel(
                    name='Member',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('member_id', models.CharField(default='', editable=False, max_length=10, unique=True)),
                        ('name', models.CharField(max_length=200)),
                        ('email', models.EmailField(max_length=254, unique=True)),
                        ('phone', models.CharField(blank=True, max_length=20)),
                        ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female')], max_length=10)),
                        ('year_of_birth', models.PositiveSmallIntegerField(blank=True, null=True)),
                        ('experience_level', models.CharField(choices=[('junior', 'Junior'), ('mid', 'Mid'), ('senior', 'Senior'), ('for_fun', 'For Fun')], max_length=10)),
                        ('primary_language', models.CharField(choices=[('python', 'Python'), ('javascript', 'JavaScript'), ('typescript', 'TypeScript'), ('java', 'Java'), ('csharp', 'C#'), ('cpp', 'C++'), ('c', 'C'), ('go', 'Go'), ('rust', 'Rust'), ('php', 'PHP'), ('ruby', 'Ruby'), ('swift', 'Swift'), ('kotlin', 'Kotlin'), ('dart', 'Dart'), ('r', 'R'), ('sql', 'SQL'), ('other', 'Other')], max_length=20)),
                        ('receive_regular_updates', models.BooleanField(default=False, help_text='Receive regular community updates')),
                        ('receive_email_communications', models.BooleanField(default=False, help_text='Receive email communications about events and announcements')),
                        ('joined_at', models.DateTimeField(auto_now_add=True)),
                    ],
                    options={
                        'db_table': 'app_member',
                    },
                ),
            ],
            database_operations=[],
        ),
    ]
