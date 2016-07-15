from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from guardian.shortcuts import assign_perm

from apps.boxes.factories import StaffFactory, BoxFactory, UserFactory
from apps.boxes.models import Box


class BoxModelTestCase(TestCase):

    def check_perms(self, user, box, perms):
        self.assertEqual(box.get_perms_for_user(user), perms,
                         msg="User doesn't have right perms to '{}' box."
                         .format(box.visibility))

    def test_get_perms_for_staff(self):
        user = StaffFactory()
        perms = ['boxes.pull_box', 'boxes.push_box',
                 'boxes.update_box', 'boxes.delete_box']
        for visibility, _ in Box.VISIBILITY_CHOICES:
            box = BoxFactory(visibility=visibility)
            self.check_perms(user, box, perms)

    def test_get_perms_for_owner(self):
        user = UserFactory()
        perms = ['boxes.pull_box', 'boxes.push_box',
                 'boxes.update_box', 'boxes.delete_box']
        for visibility, _ in Box.VISIBILITY_CHOICES:
            box = BoxFactory(visibility=visibility, owner=user)
            self.check_perms(user, box, perms)

    def test_get_perms_for_anonymous(self):
        user = AnonymousUser()

        box = BoxFactory(visibility=Box.PRIVATE)
        self.check_perms(user, box, [])

        box = BoxFactory(visibility=Box.USERS)
        self.check_perms(user, box, [])

        box = BoxFactory(visibility=Box.PUBLIC)
        self.check_perms(user, box, ['boxes.pull_box'])

    def test_get_perms_for_authenticated(self):
        user = UserFactory()

        box = BoxFactory(visibility=Box.PRIVATE)
        self.check_perms(user, box, [])

        box = BoxFactory(visibility=Box.USERS)
        self.check_perms(user, box, ['boxes.pull_box'])

        box = BoxFactory(visibility=Box.PUBLIC)
        self.check_perms(user, box, ['boxes.pull_box'])

    def test_get_perms_for_user_with_pull_access(self):
        user = UserFactory()

        box = BoxFactory(visibility=Box.PRIVATE)
        assign_perm('pull_box', user, box)
        self.check_perms(user, box, ['boxes.pull_box'])

        box = BoxFactory(visibility=Box.USERS)
        assign_perm('pull_box', user, box)
        self.check_perms(user, box, ['boxes.pull_box'])

        box = BoxFactory(visibility=Box.PUBLIC)
        assign_perm('pull_box', user, box)
        self.check_perms(user, box, ['boxes.pull_box'])

    def test_get_perms_for_user_with_push_access(self):
        user = UserFactory()

        box = BoxFactory(visibility=Box.PRIVATE)
        assign_perm('pull_box', user, box)
        assign_perm('push_box', user, box)
        self.check_perms(user, box, ['boxes.pull_box', 'boxes.push_box'])

        box = BoxFactory(visibility=Box.USERS)
        assign_perm('pull_box', user, box)
        assign_perm('push_box', user, box)
        self.check_perms(user, box, ['boxes.pull_box', 'boxes.push_box'])

        box = BoxFactory(visibility=Box.PUBLIC)
        assign_perm('pull_box', user, box)
        assign_perm('push_box', user, box)
        self.check_perms(user, box, ['boxes.pull_box', 'boxes.push_box'])

    @patch('apps.boxes.models.Box.get_perms_for_user')
    def test_user_has_perms(self, mock_get_perms):
        box = BoxFactory()

        mock_get_perms.return_value = []
        perms = ['boxes.pull_box']
        self.assertFalse(box.user_has_perms(perms, 'user'))

        mock_get_perms.return_value = ['boxes.pull_box']
        perms = ['boxes.pull_box', 'boxes.push_box']
        self.assertFalse(box.user_has_perms(perms, 'user'))

        mock_get_perms.return_value = []
        perms = []
        self.assertTrue(box.user_has_perms(perms, 'user'))

        mock_get_perms.return_value = ['boxes.pull_box']
        perms = ['boxes.pull_box']
        self.assertTrue(box.user_has_perms(perms, 'user'))

        mock_get_perms.return_value = ['boxes.pull_box', 'boxes.push_box']
        perms = ['boxes.pull_box']
        self.assertTrue(box.user_has_perms(perms, 'user'))

    def test_get_boxes_for_staff(self):
        user = StaffFactory()

        b1 = BoxFactory(visibility=Box.PRIVATE)
        b2 = BoxFactory(visibility=Box.USERS)
        b3 = BoxFactory(visibility=Box.PUBLIC)

        self.assertListEqual(list(Box.objects.for_user(user)), [b1, b2, b3])

    def test_get_boxes_for_anonymous(self):
        user = AnonymousUser()

        b1 = BoxFactory(visibility=Box.PRIVATE)
        b2 = BoxFactory(visibility=Box.USERS)
        b3 = BoxFactory(visibility=Box.PUBLIC)

        self.assertListEqual(list(Box.objects.for_user(user)), [b3])

    def test_get_boxes_for_authenticated(self):
        user = UserFactory()

        b1 = BoxFactory(visibility=Box.PRIVATE)
        b2 = BoxFactory(visibility=Box.PRIVATE, owner=user)
        b3 = BoxFactory(visibility=Box.PRIVATE)
        assign_perm('pull_box', user, b3)
        assign_perm('push_box', user, b3)
        b4 = BoxFactory(visibility=Box.PRIVATE)
        assign_perm('pull_box', user, b4)
        b5 = BoxFactory(visibility=Box.USERS)
        b6 = BoxFactory(visibility=Box.PUBLIC)

        self.assertListEqual(list(Box.objects.for_user(user)),
                             [b2, b3, b4, b5, b6])
