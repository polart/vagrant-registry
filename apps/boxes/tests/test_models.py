from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from apps.boxes.models import Box, BoxMember
from apps.factories import StaffFactory, BoxFactory, UserFactory


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

        box = BoxFactory(visibility=Box.USERS)
        self.check_perms(user, box, '')

        box = BoxFactory(visibility=Box.PUBLIC)
        self.check_perms(user, box, BoxMember.PERM_R)

    def test_get_perms_for_authenticated(self):
        user = UserFactory()

        box = BoxFactory(visibility=Box.PRIVATE)
        self.check_perms(user, box, '')

        box = BoxFactory(visibility=Box.USERS)
        self.check_perms(user, box, BoxMember.PERM_R)

        box = BoxFactory(visibility=Box.PUBLIC)
        self.check_perms(user, box, BoxMember.PERM_R)

    def test_get_perms_for_user_with_pull_access(self):
        user = UserFactory()

        box = BoxFactory(visibility=Box.PRIVATE)
        box.share_with(user, BoxMember.PERM_R)
        self.check_perms(user, box, BoxMember.PERM_R)

        box = BoxFactory(visibility=Box.USERS)
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

        box = BoxFactory(visibility=Box.USERS)
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
        b2 = BoxFactory(visibility=Box.USERS)
        b3 = BoxFactory(visibility=Box.PUBLIC)

        self.assertCountEqual(list(Box.objects.for_user(user)), [b1, b2, b3])

    def test_get_boxes_for_anonymous(self):
        user = AnonymousUser()

        b1 = BoxFactory(visibility=Box.PRIVATE)
        b2 = BoxFactory(visibility=Box.USERS)
        b3 = BoxFactory(visibility=Box.PUBLIC)

        self.assertCountEqual(list(Box.objects.for_user(user)), [b3])

    def test_get_boxes_for_authenticated(self):
        user = UserFactory()

        b1 = BoxFactory(visibility=Box.PRIVATE)
        b2 = BoxFactory(visibility=Box.PRIVATE, owner=user)
        b3 = BoxFactory(visibility=Box.PRIVATE)
        b3.share_with(user, BoxMember.PERM_RW)
        b4 = BoxFactory(visibility=Box.PRIVATE)
        b4.share_with(user, BoxMember.PERM_R)
        b5 = BoxFactory(visibility=Box.USERS)
        b6 = BoxFactory(visibility=Box.PUBLIC)

        self.assertCountEqual(list(Box.objects.for_user(user)),
                              [b2, b3, b4, b5, b6])
