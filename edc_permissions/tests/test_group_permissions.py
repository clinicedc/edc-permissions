from django.contrib.auth.models import Group
from django.test import TestCase, tag

from ..constants import (
    ACCOUNT_MANAGER, ADMINISTRATION, EVERYONE, AUDITOR,
    CLINIC, LAB, PHARMACY, PII, DEFAULT_PII_MODELS,
    DEFAULT_CODENAMES)
from ..permissions_updater import PermissionsUpdater


class TestGroupPermissions(TestCase):

    codenames = DEFAULT_CODENAMES

    permissions_updater_cls = PermissionsUpdater

    pii_models = DEFAULT_PII_MODELS

    def setUp(self):
        self.perms = self.permissions_updater_cls(verbose=False)

    def compare_codenames(self, group_name):
        """Compare the codenames of group.permissions to
        a fixed list of codenames.
        """
        group = Group.objects.get(name=group_name)
        codenames = [
            p.codename for p in group.permissions.all().order_by('codename')]
        self.assertEqual(codenames, self.codenames[group_name])

    def test_account_manager(self):
        self.compare_codenames(ACCOUNT_MANAGER)

    def test_everyone(self):
        self.compare_codenames(EVERYONE)

    def test_auditor(self):
        self.compare_codenames(AUDITOR)

    def test_clinic(self):
        self.compare_codenames(CLINIC)

    def test_lab(self):
        self.compare_codenames(LAB)

    def test_pharmacy(self):
        self.compare_codenames(PHARMACY)

    def test_pii(self):
        self.compare_codenames(PII)
        self.perms.pii_models
        self.assertEqual(self.perms.pii_models, self.pii_models)

    def test_administration(self):
        self.compare_codenames(ADMINISTRATION)
