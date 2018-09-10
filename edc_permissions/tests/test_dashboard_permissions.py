from django.contrib.auth.models import Permission
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, tag

from ..constants import LAB_DASHBOARD_CODENAMES
from ..permissions_updater import (
    PermissionsUpdater, PermissionsUpdaterError, DUPLICATE_CODENAME)
from unittest.case import skip


class TestDashboardPermissions(TestCase):

    def setUp(self):
        self.perms = PermissionsUpdater(verbose=False)

    def test_default_dashboard_codenames(self):

        class MyPermissionsUpdater(PermissionsUpdater):
            extra_dashboard_codenames = []

        MyPermissionsUpdater(verbose=True)

        for codename, name in LAB_DASHBOARD_CODENAMES:
            try:
                Permission.objects.get(codename=codename, name=name)
            except ObjectDoesNotExist:
                self.fail(
                    f'Permission unexpectedly does not exist. Got {(codename, name)}')

    def test_adds_dashboard_codenames(self):

        codename = ('view_erik', 'View Erik')

        class MyPermissionsUpdater(PermissionsUpdater):
            extra_dashboard_codenames = {'ERIK': [codename]}

        MyPermissionsUpdater(verbose=True)

        try:
            Permission.objects.get(codename=codename[0])
        except ObjectDoesNotExist:
            self.fail(
                f'Permission unexpectedly does not exist. Got {codename}')

    def test_detects_duplicate_dashboard_codenames(self):

        codenames = [('view_erik', 'View Erik'), ('view_erik', 'View Erik')]

        class MyPermissionsUpdater(PermissionsUpdater):
            extra_dashboard_codenames = {'ERIK': codenames}

        with self.assertRaises(PermissionsUpdaterError) as cm:
            MyPermissionsUpdater(verbose=True)
        self.assertEqual(cm.exception.code, DUPLICATE_CODENAME)
