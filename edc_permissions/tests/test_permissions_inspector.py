from django.test import TestCase, tag

from ..constants import DEFAULT_GROUP_NAMES, DEFAULT_CODENAMES
from ..permissions_inspector import PermissionsInspector
from ..permissions_updater import PermissionsUpdater


class TestPermissionsInspector(TestCase):

    def setUp(self):
        self.perms = PermissionsUpdater(verbose=False)

    @tag('1')
    def test_init(self):
        inspector = PermissionsInspector()
        for group_name in DEFAULT_GROUP_NAMES:
            self.assertEqual(
                DEFAULT_CODENAMES.get(group_name),
                inspector.get_codenames(group_name))
