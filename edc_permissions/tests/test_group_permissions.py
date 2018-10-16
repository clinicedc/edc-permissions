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

    def test_account_manager(self):
        self.inspector.compare_codenames(group_name=ACCOUNT_MANAGER)

    def test_administration(self):
        self.inspector.compare_codenames(group_name=ADMINISTRATION)

    def test_auditor(self):
        self.inspector.compare_codenames(group_name=AUDITOR)

    def test_everyone(self):
        self.inspector.compare_codenames(group_name=EVERYONE)

    def test_clinic(self):
        self.inspector.compare_codenames(group_name=CLINIC)

    def test_lab(self):
        self.inspector.compare_codenames(group_name=LAB)

    def test_export(self):
        self.inspector.compare_codenames(group_name=EXPORT)

    def test_pharmacy(self):
        self.inspector.compare_codenames(group_name=PHARMACY)

    def test_pii(self):
        self.inspector.compare_codenames(group_name=PII)
        self.assertEqual(self.updater.pii_models, self.inspector.pii_models)

    def test_pii_view(self):
        self.inspector.compare_codenames(group_name=PII_VIEW)
