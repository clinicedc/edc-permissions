from django.contrib.auth.models import Group
from django.test import TestCase, tag

from ..constants import (
    ACCOUNT_MANAGER, ADMINISTRATION, EVERYONE, AUDITOR,
    CLINIC, LAB, PHARMACY, PII, PII_VIEW, EXPORT)
from ..permissions_inspector import PermissionsInspector
from ..permissions_updater import PermissionsUpdater


class TestGroupPermissions(TestCase):

    permissions_updater_cls = PermissionsUpdater

    def setUp(self):
        self.updater = self.permissions_updater_cls(verbose=False)
        self.inspector = PermissionsInspector()

    def compare_codenames(self, group_name):
        """Compare the codenames of group.permissions to
        a fixed list of codenames.
        """
        group = Group.objects.get(name=group_name)
        codenames = [
            p.codename for p in group.permissions.all().order_by('codename')]
        self.assertEqual(codenames, self.inspector.get_codenames(group_name))

    def test_account_manager(self):
        self.compare_codenames(ACCOUNT_MANAGER)

    def test_administration(self):
        self.compare_codenames(ADMINISTRATION)

    def test_auditor(self):
        self.compare_codenames(AUDITOR)

    def test_everyone(self):
        self.compare_codenames(EVERYONE)

    def test_clinic(self):
        self.compare_codenames(CLINIC)

    def test_lab(self):
        self.compare_codenames(LAB)

    def test_export(self):
        self.compare_codenames(EXPORT)

    def test_pharmacy(self):
        self.compare_codenames(PHARMACY)

    def test_pii(self):
        self.compare_codenames(PII)
        self.assertEqual(self.updater.pii_models, self.inspector.pii_models)

    def test_pii_view(self):
        self.compare_codenames(PII_VIEW)
