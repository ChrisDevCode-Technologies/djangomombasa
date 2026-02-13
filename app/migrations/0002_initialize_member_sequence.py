# Data migration to initialize MemberIdSequence from existing members

from django.db import migrations


def initialize_sequence(apps, schema_editor):
    """
    Set the sequence to continue from the highest existing member_id.
    Parses 'DM-XXX' format to find the max number.
    """
    Member = apps.get_model('app', 'Member')
    MemberIdSequence = apps.get_model('app', 'MemberIdSequence')

    max_number = -1
    for member in Member.objects.all():
        if member.member_id and member.member_id.startswith('DM-'):
            try:
                num = int(member.member_id[3:])
                max_number = max(max_number, num)
            except ValueError:
                pass

    # Next number is max + 1, or 0 if no members exist
    next_number = max_number + 1 if max_number >= 0 else 0

    # Create or update the singleton sequence row
    MemberIdSequence.objects.update_or_create(
        pk=1,
        defaults={'next_number': next_number}
    )


def reverse_sequence(apps, schema_editor):
    """Remove the sequence row on reverse migration."""
    MemberIdSequence = apps.get_model('app', 'MemberIdSequence')
    MemberIdSequence.objects.filter(pk=1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(initialize_sequence, reverse_sequence),
    ]
