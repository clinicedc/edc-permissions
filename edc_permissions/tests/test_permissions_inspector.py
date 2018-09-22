from django.contrib.auth.models import Group
from django.test import TestCase, tag
from pprint import pprint

from ..constants import DEFAULT_GROUP_NAMES, DEFAULT_CODENAMES, EVERYONE
from ..permissions_inspector import INVALID_GROUP_NAME, MISSING_DEFAULT_GROUP
from ..permissions_inspector import MISSING_DEFAULT_CODENAME
from ..permissions_inspector import PermissionsInspector, PermissionsInspectorError
from ..permissions_updater import PermissionsUpdater


class TestPermissionsInspector(TestCase):

    def setUp(self):
        Group.objects.filter(name__in=DEFAULT_GROUP_NAMES).delete()
        self.perms = PermissionsUpdater(verbose=False)

    def test_init(self):
        inspector = PermissionsInspector()
        for group_name in DEFAULT_GROUP_NAMES:
            # print(f'compare {group_name} to default codenames')
            # print(inspector.get_codenames(group_name))
            if DEFAULT_CODENAMES.get(group_name) != inspector.get_codenames(group_name):
                pprint(DEFAULT_CODENAMES.get(group_name))
                pprint(inspector.get_codenames(group_name))
            self.assertEqual(
                DEFAULT_CODENAMES.get(group_name),
                inspector.get_codenames(group_name))

    def test_invalid_group_name(self):
        with self.assertRaises(PermissionsInspectorError) as cm:
            inspector = PermissionsInspector()
            inspector.get_codenames('BLAH')
        # print(cm.exception.message)
        self.assertEqual(cm.exception.code, INVALID_GROUP_NAME)

    def test_missing_default_group_name(self):
        Group.objects.get(name=EVERYONE).delete()
        with self.assertRaises(PermissionsInspectorError) as cm:
            PermissionsInspector()
        self.assertEqual(cm.exception.code, MISSING_DEFAULT_GROUP)

    def test_missing_default_codename(self):
        group = Group.objects.get(name=EVERYONE)
        group.permissions.all().delete()
        with self.assertRaises(PermissionsInspectorError) as cm:
            PermissionsInspector()
        self.assertEqual(cm.exception.code, MISSING_DEFAULT_CODENAME)
