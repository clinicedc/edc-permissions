from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, tag
from edc_lab_dashboard.dashboard_urls import dashboard_urls as lab_dashboard_urls
from edc_navbar import NavbarItem, site_navbars, Navbar

from ..permissions_updater import PermissionsUpdater
from edc_permissions.permissions_updater import PermissionsUpdaterError

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


class TestPermissions(TestCase):

    def setUp(self):
        self.perms = PermissionsUpdater(verbose=False)

    def test_creates_groups(self):
        for group_name in self.perms.group_names:
            try:
                Group.objects.get(name=group_name)
            except ObjectDoesNotExist:
                self.fail(
                    f'Group unexpectedly not created. Got {group_name} ')

    def test_account_manager(self):
        group = Group.objects.get(name='ACCOUNT_MANAGER')
        codenames = [
            p.codename for p in group.permissions.all().order_by('codename')]
        self.assertEqual(
            codenames, ['add_group',
                        'add_permission',
                        'add_user',
                        'add_userprofile',
                        'change_group',
                        'change_permission',
                        'change_user',
                        'change_userprofile',
                        'delete_group',
                        'delete_permission',
                        'delete_user',
                        'delete_userprofile',
                        'view_group',
                        'view_permission',
                        'view_user',
                        'view_userprofile'])

    def test_everyone(self):
        group = Group.objects.get(name='EVERYONE')
        codenames = [
            p.codename for p in group.permissions.all().order_by('codename')]
        self.assertEqual(
            codenames, [
                'view_group',
                'view_logentry',
                'view_permission',
                'view_site',
                'view_user',
                'view_userprofile'])

    def test_auditor(self):
        group = Group.objects.get(name='AUDITOR')
        codenames = [
            p.codename for p in group.permissions.all().order_by('codename')]
        self.assertEqual(
            codenames, [
                'nav_lab_requisition',
                'nav_lab_section',
                'view_actionitem',
                'view_actionitemupdate',
                'view_actiontype',
                'view_aliquot',
                'view_appointment',
                'view_box',
                'view_boxitem',
                'view_boxtype',
                'view_consignee',
                'view_historicalactionitem',
                'view_historicalactionitemupdate',
                'view_historicalaliquot',
                'view_historicalappointment',
                'view_historicalbox',
                'view_historicalboxitem',
                'view_historicalconsignee',
                'view_historicalmanifest',
                'view_historicalorder',
                'view_historicalresult',
                'view_historicalresultitem',
                'view_historicalshipper',
                'view_manifest',
                'view_manifestitem',
                'view_order',
                'view_panel',
                'view_reference',
                'view_registeredsubject',
                'view_result',
                'view_resultitem',
                'view_shipper',
                'view_subjectlocator',
                'view_subjectoffstudy'])

    def test_clinic(self):
        group = Group.objects.get(name='CLINIC')
        codenames = [
            p.codename for p in group.permissions.all().order_by('codename')]
        self.assertEqual(
            codenames, ['add_actionitem',
                        'add_actionitemupdate',
                        'add_actiontype',
                        'add_appointment',
                        'add_reference',
                        'change_actionitem',
                        'change_actionitemupdate',
                        'change_actiontype',
                        'change_appointment',
                        'change_reference',
                        'delete_actionitem',
                        'delete_actionitemupdate',
                        'delete_actiontype',
                        'delete_reference',
                        'nav_lab_requisition',
                        'nav_lab_section',
                        'view_actionitem',
                        'view_actionitemupdate',
                        'view_actiontype',
                        'view_appointment',
                        'view_historicalactionitem',
                        'view_historicalactionitemupdate',
                        'view_historicalappointment',
                        'view_reference'])

    def test_lab(self):
        group = Group.objects.get(name='LAB')
        codenames = [
            p.codename for p in group.permissions.all().order_by('codename')]
        self.assertEqual(
            codenames, [
                'add_aliquot',
                'add_box',
                'add_boxitem',
                'add_boxtype',
                'add_consignee',
                'add_manifest',
                'add_manifestitem',
                'add_order',
                'add_panel',
                'add_result',
                'add_resultitem',
                'add_shipper',
                'change_aliquot',
                'change_box',
                'change_boxitem',
                'change_boxtype',
                'change_consignee',
                'change_manifest',
                'change_manifestitem',
                'change_order',
                'change_panel',
                'change_result',
                'change_resultitem',
                'change_shipper',
                'delete_aliquot',
                'delete_box',
                'delete_boxitem',
                'delete_boxtype',
                'delete_consignee',
                'delete_manifest',
                'delete_manifestitem',
                'delete_order',
                'delete_panel',
                'delete_result',
                'delete_resultitem',
                'delete_shipper',
                'nav_lab_aliquot',
                'nav_lab_manifest',
                'nav_lab_pack',
                'nav_lab_process',
                'nav_lab_receive',
                'nav_lab_requisition',
                'nav_lab_section',
                'view_aliquot',
                'view_box',
                'view_boxitem',
                'view_boxtype',
                'view_consignee',
                'view_historicalaliquot',
                'view_historicalbox',
                'view_historicalboxitem',
                'view_historicalconsignee',
                'view_historicalmanifest',
                'view_historicalorder',
                'view_historicalresult',
                'view_historicalresultitem',
                'view_historicalshipper',
                'view_manifest',
                'view_manifestitem',
                'view_order',
                'view_panel',
                'view_result',
                'view_resultitem',
                'view_shipper'])

    def test_pharmacy(self):
        group = Group.objects.get(name='PHARMACY')
        codenames = [
            p.codename for p in group.permissions.all().order_by('codename')]
        self.assertEqual(
            codenames, [
                'add_appointment',
                'add_dispenseditem',
                'add_dosageguideline',
                'add_medication',
                'add_prescription',
                'add_prescriptionitem',
                'change_appointment',
                'change_dispenseditem',
                'change_dosageguideline',
                'change_medication',
                'change_prescription',
                'change_prescriptionitem',
                'delete_appointment',
                'delete_dispenseditem',
                'delete_dosageguideline',
                'delete_medication',
                'delete_prescription',
                'delete_prescriptionitem',
                'nav_pharmacy_section',
                'view_appointment',
                'view_dispenseditem',
                'view_dosageguideline',
                'view_medication',
                'view_prescription',
                'view_prescriptionitem'])

    def test_pii(self):
        group = Group.objects.get(name='PII')
        codenames = [
            p.codename for p in group.permissions.all().order_by('codename')]
        self.assertEqual(self.perms.pii_models, [
                         'edc_locator.subjectlocator',
                         'edc_registration.registeredsubject'])
        self.assertEqual(
            codenames, ['add_subjectlocator',
                        'change_subjectlocator',
                        'delete_subjectlocator',
                        'display_dob',
                        'display_firstname',
                        'display_identity',
                        'display_initials',
                        'display_lastname',
                        'view_registeredsubject',
                        'view_subjectlocator'])

    def test_administration(self):
        group = Group.objects.get(name='ADMINISTRATION')
        codenames = [
            p.codename for p in group.permissions.all().order_by('codename')]
        self.assertEqual(
            codenames, ['nav_administration'])

    def test_raises_if_missing_group_permissions_method(self):

        class MyPermissionsUpdater(PermissionsUpdater):
            group_names = ['ERIK']

        with self.assertRaises(PermissionsUpdaterError) as cm:
            MyPermissionsUpdater(verbose=False)
        self.assertEqual(cm.exception.code, 'missing_method')

    def test_raises_if_group_not_created(self):

        class MyPermissionsUpdater(PermissionsUpdater):
            group_names = ['ERIK']

            def update_erik_group_permissions(self):
                pass

        MyPermissionsUpdater(verbose=True)
        try:
            Group.objects.get(name='ERIK')
        except ObjectDoesNotExist:
            self.fail('group was unexpectedly not created')

    def test_raises_if_invalid_app_label(self):

        class MyPermissionsUpdater(PermissionsUpdater):
            group_names = ['ERIK']
            pii_models = ['blah_app_label1.piimodel']
            auditor_app_labels = ['blah_app_label2']

            def update_erik_group_permissions(self):
                pass

        with self.assertRaises(PermissionsUpdaterError) as cm:
            MyPermissionsUpdater(verbose=False)
        self.assertEqual(cm.exception.code, 'lookup')

    def test_raises_if_invalid_navbar_codename(self):

        class MyPermissionsUpdater(PermissionsUpdater):
            group_names = ['ERIK']
            pii_models = ['edc_permissions.piimodel']
            auditor_app_labels = ['edc_permissions']

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
            group_names = ['ERIK']
            pii_models = ['edc_permissions.piimodel']
            auditor_app_labels = ['edc_permissions']

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
