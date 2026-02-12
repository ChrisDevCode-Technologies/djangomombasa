from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest import skipIf
from django.conf import settings
from django.test import TestCase, TransactionTestCase
from django.db import connection

from app.models import Member, MemberIdSequence

_using_sqlite = settings.DATABASES['default']['ENGINE'].endswith('sqlite3')


class MemberIdSequenceTest(TestCase):
    """Tests for the MemberIdSequence model."""

    def test_get_next_id_starts_at_zero(self):
        """First ID should be DM-000."""
        member_id = MemberIdSequence.get_next_id()
        self.assertEqual(member_id, 'DM-000')

    def test_get_next_id_increments(self):
        """Sequential calls should increment the ID."""
        id1 = MemberIdSequence.get_next_id()
        id2 = MemberIdSequence.get_next_id()
        id3 = MemberIdSequence.get_next_id()

        self.assertEqual(id1, 'DM-000')
        self.assertEqual(id2, 'DM-001')
        self.assertEqual(id3, 'DM-002')

    def test_get_next_id_formatting(self):
        """IDs should be zero-padded to 3 digits."""
        # Set sequence to a higher number
        MemberIdSequence.objects.update_or_create(pk=1, defaults={'next_number': 42})
        member_id = MemberIdSequence.get_next_id()
        self.assertEqual(member_id, 'DM-042')

    def test_sequence_persists(self):
        """Sequence value should persist after get_next_id calls."""
        MemberIdSequence.get_next_id()
        MemberIdSequence.get_next_id()
        MemberIdSequence.get_next_id()

        seq = MemberIdSequence.objects.get(pk=1)
        self.assertEqual(seq.next_number, 3)


class MemberModelTest(TestCase):
    """Tests for Member model ID generation."""

    def _create_member(self, name, email):
        """Helper to create a member with required fields."""
        return Member.objects.create(
            name=name,
            email=email,
            gender=Member.Gender.MALE,
            experience_level=Member.ExperienceLevel.JUNIOR,
            primary_language=Member.PrimaryLanguage.PYTHON,
        )

    def test_member_gets_auto_id_on_create(self):
        """New member should get auto-generated member_id."""
        member = self._create_member('Test User', 'test@example.com')
        self.assertTrue(member.member_id.startswith('DM-'))
        self.assertEqual(len(member.member_id), 6)  # DM-XXX

    def test_sequential_members_get_sequential_ids(self):
        """Members created in sequence should have sequential IDs."""
        m1 = self._create_member('User 1', 'user1@example.com')
        m2 = self._create_member('User 2', 'user2@example.com')
        m3 = self._create_member('User 3', 'user3@example.com')

        self.assertEqual(m1.member_id, 'DM-000')
        self.assertEqual(m2.member_id, 'DM-001')
        self.assertEqual(m3.member_id, 'DM-002')

    def test_member_id_not_changed_on_update(self):
        """Existing member_id should not change on save."""
        member = self._create_member('Test User', 'test@example.com')
        original_id = member.member_id

        member.name = 'Updated Name'
        member.save()

        member.refresh_from_db()
        self.assertEqual(member.member_id, original_id)

    def test_member_id_unique_constraint(self):
        """Database should enforce unique member_id."""
        self._create_member('User 1', 'user1@example.com')

        # Verify the unique constraint exists
        member = Member(
            name='User 2',
            email='user2@example.com',
            gender=Member.Gender.MALE,
            experience_level=Member.ExperienceLevel.JUNIOR,
            primary_language=Member.PrimaryLanguage.PYTHON,
            member_id='DM-000',  # Duplicate ID
        )
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            member.save()

    def test_deletion_does_not_reuse_ids(self):
        """Deleting a member should not cause ID reuse."""
        m1 = self._create_member('User 1', 'user1@example.com')
        m2 = self._create_member('User 2', 'user2@example.com')

        self.assertEqual(m1.member_id, 'DM-000')
        self.assertEqual(m2.member_id, 'DM-001')

        # Delete first member
        m1.delete()

        # New member should get next ID, not reuse DM-000
        m3 = self._create_member('User 3', 'user3@example.com')
        self.assertEqual(m3.member_id, 'DM-002')


class ConcurrentMemberCreationTest(TransactionTestCase):
    """
    Tests for race-safe member ID generation under concurrent creation.
    Uses TransactionTestCase to allow testing with real database transactions.
    """

    def _create_member_in_thread(self, index):
        """Create a member and return its ID. For use in threads."""
        try:
            # Each thread needs its own connection
            connection.close()
            member = Member.objects.create(
                name=f'Concurrent User {index}',
                email=f'concurrent{index}@example.com',
                gender=Member.Gender.MALE,
                experience_level=Member.ExperienceLevel.JUNIOR,
                primary_language=Member.PrimaryLanguage.PYTHON,
            )
            return member.member_id
        finally:
            connection.close()

    def test_rapid_sequential_creation(self):
        """Rapidly creating members should produce unique IDs."""
        members = []
        for i in range(20):
            member = Member.objects.create(
                name=f'Rapid User {i}',
                email=f'rapid{i}@example.com',
                gender=Member.Gender.MALE,
                experience_level=Member.ExperienceLevel.JUNIOR,
                primary_language=Member.PrimaryLanguage.PYTHON,
            )
            members.append(member)

        # All IDs should be unique
        member_ids = [m.member_id for m in members]
        self.assertEqual(len(member_ids), len(set(member_ids)))

        # IDs should be sequential
        expected_ids = [f'DM-{i:03d}' for i in range(20)]
        self.assertEqual(member_ids, expected_ids)

    @skipIf(_using_sqlite, "SQLite does not support concurrent writes")
    def test_concurrent_creation_no_duplicates(self):
        """
        Concurrent member creation should not produce duplicate IDs.
        This tests the race condition fix.
        """
        num_threads = 10
        member_ids = []
        errors = []

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(self._create_member_in_thread, i)
                for i in range(num_threads)
            ]

            for future in as_completed(futures):
                try:
                    member_id = future.result()
                    member_ids.append(member_id)
                except Exception as e:
                    errors.append(str(e))

        # No errors should have occurred
        self.assertEqual(errors, [], f"Errors during concurrent creation: {errors}")

        # All IDs should be unique
        self.assertEqual(
            len(member_ids),
            len(set(member_ids)),
            f"Duplicate IDs found: {member_ids}"
        )

        # Should have created all members
        self.assertEqual(len(member_ids), num_threads)

        # Verify in database
        db_count = Member.objects.count()
        self.assertEqual(db_count, num_threads)

        # All member_ids in DB should be unique
        db_ids = list(Member.objects.values_list('member_id', flat=True))
        self.assertEqual(len(db_ids), len(set(db_ids)))
