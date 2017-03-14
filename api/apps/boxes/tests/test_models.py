from io import StringIO
from unittest.mock import patch
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.utils import timezone

from apps.boxes.models import Box, BoxMember, BoxUpload, BoxProvider
from apps.factories import StaffFactory, BoxFactory, UserFactory, BoxProviderFactory, BoxUploadFactory


class BoxModelTestCase(TestCase):

    def check_perms(self, user, box, perms):
        self.assertEqual(box.get_perms_for_user(user), perms,
                         msg="User doesn't have right perms to '{}' box."
                         .format(box.visibility))

    def test_get_perms_for_staff(self):
        user = StaffFactory()
        for visibility, _ in Box.VISIBILITY_CHOICES:
            box = BoxFactory(visibility=visibility)
            self.check_perms(user, box, BoxMember.PERM_OWNER_OR_STAFF)

    def test_get_perms_for_owner(self):
        user = UserFactory()
        for visibility, _ in Box.VISIBILITY_CHOICES:
            box = BoxFactory(visibility=visibility, owner=user)
            self.check_perms(user, box, BoxMember.PERM_OWNER_OR_STAFF)

    def test_get_perms_for_anonymous(self):
        user = AnonymousUser()

        box = BoxFactory(visibility=Box.PRIVATE)
        self.check_perms(user, box, '')

        box = BoxFactory(visibility=Box.PUBLIC)
        self.check_perms(user, box, BoxMember.PERM_R)

    def test_get_perms_for_authenticated(self):
        user = UserFactory()

        box = BoxFactory(visibility=Box.PRIVATE)
        self.check_perms(user, box, '')

        box = BoxFactory(visibility=Box.PUBLIC)
        self.check_perms(user, box, BoxMember.PERM_R)

    def test_get_perms_for_user_with_pull_access(self):
        user = UserFactory()

        box = BoxFactory(visibility=Box.PRIVATE)
        box.share_with(user, BoxMember.PERM_R)
        self.check_perms(user, box, BoxMember.PERM_R)

        box = BoxFactory(visibility=Box.PUBLIC)
        box.share_with(user, BoxMember.PERM_R)
        self.check_perms(user, box, BoxMember.PERM_R)

    def test_get_perms_for_user_with_push_access(self):
        user = UserFactory()

        box = BoxFactory(visibility=Box.PRIVATE)
        box.share_with(user, BoxMember.PERM_RW)
        self.check_perms(user, box, BoxMember.PERM_RW)

        box = BoxFactory(visibility=Box.PUBLIC)
        box.share_with(user, BoxMember.PERM_RW)
        self.check_perms(user, box, BoxMember.PERM_RW)

    @patch('apps.boxes.models.Box.get_perms_for_user')
    def test_user_has_perms(self, mock_get_perms):
        box = BoxFactory()

        mock_get_perms.return_value = ''
        self.assertFalse(box.user_has_perms('user', 'R'))

        mock_get_perms.return_value = BoxMember.PERM_R
        self.assertFalse(box.user_has_perms('user', 'RW'))

        mock_get_perms.return_value = ''
        self.assertTrue(box.user_has_perms('user', ''))

        mock_get_perms.return_value = BoxMember.PERM_R
        self.assertTrue(box.user_has_perms('user', 'R'))

        mock_get_perms.return_value = BoxMember.PERM_RW
        self.assertTrue(box.user_has_perms('user', 'R'))

    def test_get_boxes_for_staff(self):
        user = StaffFactory()

        b1 = BoxFactory(visibility=Box.PRIVATE)
        b2 = BoxFactory(visibility=Box.PUBLIC)

        self.assertCountEqual(list(Box.objects.for_user(user)), [b1, b2])

    def test_get_boxes_for_anonymous(self):
        user = AnonymousUser()

        b1 = BoxFactory(visibility=Box.PRIVATE)
        b2 = BoxFactory(visibility=Box.PUBLIC)

        self.assertCountEqual(list(Box.objects.for_user(user)), [b2])

    def test_get_boxes_for_authenticated(self):
        user = UserFactory()

        b1 = BoxFactory(visibility=Box.PRIVATE)
        b2 = BoxFactory(visibility=Box.PRIVATE, owner=user)
        b3 = BoxFactory(visibility=Box.PRIVATE)
        b3.share_with(user, BoxMember.PERM_RW)
        b4 = BoxFactory(visibility=Box.PRIVATE)
        b4.share_with(user, BoxMember.PERM_R)
        b5 = BoxFactory(visibility=Box.PUBLIC)

        self.assertCountEqual(
            list(Box.objects.for_user(user)),
            [b2, b3, b4, b5]
        )


class BoxUploadTestCase(TestCase):

    def test_chunk_cannot_be_appended_to_completed_upload(self):
        bu = BoxUploadFactory(status=BoxUpload.COMPLETED)
        with self.assertRaises(AssertionError):
            bu.append_chunk('chunk')

    def test_chunk_cannot_be_appended_to_expired_upload(self):
        date_created = timezone.now() - timedelta(
            hours=settings.BOX_UPLOAD_EXPIRE_AFTER + 1
        )
        bu = BoxUploadFactory(status=BoxUpload.STARTED)
        bu.date_created = date_created
        with self.assertRaises(AssertionError):
            bu.append_chunk('chunk')

    def test_box_provider_detail_filled_in_on_upload_completion(self):
        content = b'test'
        bu = BoxUploadFactory(
            file_content=content,
            provider__date_updated=timezone.now() - timedelta(hours=1),
        )
        f = StringIO(content.decode('utf8'))
        f.size = 4
        f.name = 'test.box'
        old_date_updated = bu.provider.date_updated

        self.assertEqual(bu.provider.status, BoxProvider.EMPTY)

        bu.append_chunk(f)

        self.assertEqual(bu.status, BoxUpload.COMPLETED)

        bu.provider.refresh_from_db()
        self.assertEqual(bu.provider.status, BoxProvider.FILLED_IN)
        self.assertEqual(bu.provider.file.read(), content)
        self.assertNotEqual(bu.provider.date_updated, old_date_updated)

        bu.provider.version.refresh_from_db()
        self.assertEqual(
            bu.provider.version.date_updated,
            bu.provider.date_updated
        )

        bu.provider.version.box.refresh_from_db()
        self.assertEqual(
            bu.provider.version.box.date_updated,
            bu.provider.date_updated
        )
