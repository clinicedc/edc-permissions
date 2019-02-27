from django.test import TestCase, tag

from ..constants import DEFAULT_CODENAMES
from ..permissions_inspector import PermissionsInspector
from ..permissions_updater import PermissionsUpdater


class TestGroupPermissions(TestCase):

    codenames = DEFAULT_CODENAMES

    permissions_updater_cls = PermissionsUpdater

    def setUp(self):
        self.updater = self.permissions_updater_cls(verbose=False)
        self.inspector = PermissionsInspector(
            default_codenames=self.codenames, verbose=True
        )

    @tag("compare_codenames")
    def test_codenames(self):
        for group in self.codenames:
            self.inspector.compare_codenames(group_name=group)
