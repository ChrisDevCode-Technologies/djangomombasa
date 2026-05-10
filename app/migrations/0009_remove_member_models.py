from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_member_receive_email_communications_and_more'),
        ('membership', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(name='Member'),
                migrations.DeleteModel(name='MemberIdSequence'),
            ],
            database_operations=[],
        ),
    ]
