from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, tag
from edc_lab_dashboard.dashboard_urls import dashboard_urls as lab_dashboard_urls
from edc_navbar import NavbarItem, site_navbars, Navbar

from ..permissions_updater import PermissionsUpdater, PermissionsUpdaterError

navbar = Navbar(name='ambition')

navbar.append_item(
    NavbarItem(
        name='pharmacy',
        label='Pharmacy',
        fa_icon='fas fa-medkit',
        permission_codename='nav_pharmacy_section',
        url_name=f'home_url'))

navbar.append_item(
    NavbarItem(
        name='lab',
        label='Specimens',
        fa_icon='fas fa-flask',
        permission_codename='nav_lab_section',
        url_name=lab_dashboard_urls.get('requisition_listboard_url')))

site_navbars.register(navbar)


class TestPermissionsUpdater(TestCase):

    def setUp(self):
        self.perms = PermissionsUpdater(verbose=False)

    def test_creates_groups(self):
        for group_name in self.perms.group_names:
            try:
                Group.objects.get(name=group_name)
            except ObjectDoesNotExist:
                self.fail(
                    f'Group unexpectedly not created. Got {group_name} ')

    def test_raises_if_missing_group_permissions_method(self):

        class MyPermissionsUpdater(PermissionsUpdater):
            extra_group_names = ['ERIK']

        with self.assertRaises(PermissionsUpdaterError) as cm:
            MyPermissionsUpdater(verbose=False)
        self.assertEqual(cm.exception.code, 'missing_method')

    def test_raises_if_group_not_created(self):

        class MyPermissionsUpdater(PermissionsUpdater):
            extra_group_names = ['ERIK']

            def update_erik_group_permissions(self):
                pass

        MyPermissionsUpdater(verbose=True)
        try:
            Group.objects.get(name='ERIK')
        except ObjectDoesNotExist:
            self.fail('group was unexpectedly not created')

    def test_raises_if_invalid_app_label(self):

        class MyPermissionsUpdater(PermissionsUpdater):
            extra_group_names = ['ERIK']
            extra_pii_models = ['blah_app_label1.piimodel']
            extra_auditor_app_labels = ['blah_app_label2']

            def update_erik_group_permissions(self):
                pass

        with self.assertRaises(PermissionsUpdaterError) as cm:
            MyPermissionsUpdater(verbose=False)
        self.assertEqual(cm.exception.code, 'lookup')

    def test_raises_if_invalid_navbar_codename(self):

        class MyPermissionsUpdater(PermissionsUpdater):
            extra_group_names = ['ERIK']
            extra_pii_models = ['edc_permissions.piimodel']
            extra_auditor_app_labels = ['edc_permissions']

            def update_erik_group_permissions(self):
                group = Group.objects.get(name='ERIK')
                group.permissions.clear()
                self.add_navbar_permissions(
                    group, codenames=['nav_blahblah'])

        with self.assertRaises(PermissionsUpdaterError) as cm:
            MyPermissionsUpdater(verbose=False)
        self.assertEqual(cm.exception.code, 'missing_navbar_codename')

    def test_correctly_adds_custom_codenames(self):

        class MyPermissionsUpdater(PermissionsUpdater):
            extra_group_names = ['ERIK']
            extra_pii_models = ['edc_permissions.piimodel']
            extra_auditor_app_labels = ['edc_permissions']

            def update_erik_group_permissions(self):
                group = Group.objects.get(name='ERIK')
                group.permissions.clear()
                self.add_navbar_permissions(
                    group, codenames=[
                        'nav_lab_section', 'nav_lab_requisition'])

        MyPermissionsUpdater(verbose=True)
        group = Group.objects.get(name='PII')
        codenames = [p.codename for p in group.permissions.all()]
        self.assertIn('be_happy', codenames)

        MyPermissionsUpdater(verbose=True)
        group = Group.objects.get(name='PII')
        codenames = [p.codename for p in group.permissions.all()]
        self.assertIn('be_happy', codenames)
