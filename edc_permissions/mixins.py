import sys

from django.contrib.auth.models import Group, Permission, User
from django.core.exceptions import ObjectDoesNotExist
from edc_navbar.site_navbars import site_navbars


class EdcPermissionsUpdaterMixin:

    default_group_names = [
        'ACCOUNT_MANAGER',
        'AUDITOR',
        'CLINIC',
        'EVERYONE',
        'LAB',
        'PHARMACY',
        'PII']
    default_pii_app_labels = ['edc_locator', 'edc_registration']
    default_pii_models = ['subjectlocator', 'registeredsubject']
    group_names = None
    pii_app_labels = None
    pii_models = None

    def __init__(self):
        self.pii_app_labels.extend(self.default_pii_app_labels)
        self.pii_app_labels = list(set(self.pii_app_labels))
        self.pii_models.extend(self.default_pii_models)
        self.pii_models = list(set(self.pii_models))
        self.group_names.extend(self.default_group_names)
        self.group_names = list(set(self.group_names))
        self.update_groups()
        self.update_group_permissions()

    def update_groups(self, group_names=None):
        sys.stdout.write('Adding or updating groups ...\n')
        for name in group_names:
            try:
                Group.objects.get(name=name)
            except ObjectDoesNotExist:
                Group.objects.create(name=name)
        Group.objects.exclude(name__in=self.group_names).delete()
        sys.stdout.write(
            f"  Groups are: "
            f"{', '.join([obj.name for obj in Group.objects.all().order_by('name')])}\n")

    def update_group_permissions(self, pii_app_labels=None, pii_models=None):
        sys.stdout.write('Adding or updating permissions ...\n')

        group_name = 'ACCOUNT_MANAGER'
        sys.stdout.write(f' * adding permissions to {group_name}.\n')
        group = Group.objects.get(name=group_name)
        group.permissions.clear()
        self.add_auth_permissions(group)

        group_name = 'EVERYONE'
        sys.stdout.write(f' * adding permissions to {group_name}.\n')
        group = Group.objects.get(name=group_name)
        group.permissions.clear()
        self.add_userprofile_permissions_to_active(group)

        group_name = 'AUDITOR'
        sys.stdout.write(f' * adding permissions to {group_name}.\n')
        group = Group.objects.get(name=group_name)
        for permission in Permission.objects.filter(
                content_type__app_label__in=[
                    'ambition_ae',
                    'ambition_prn',
                    'ambition_screening',
                    'ambition_subject',
                    'edc_lab'
                    'edc_offstudy',
                ],
                content_type__model__startswith='view'):
            group.permissions.add(permission)
        self.add_edc_action_permissions(group)
        self.add_edc_appointment_permissions(group)
        self.add_pii_permissions(
            group,
            app_labels=pii_app_labels,
            pii_models=self.pii_models,
            view_only=True)
        self.add_navbar_permissions(
            group, codenames=['default_administration', 'edc_lab', 'lab_requisition'])

        group_name = 'PII'
        sys.stdout.write(f' * adding permissions to {group_name}.\n')
        group = Group.objects.get(name=group_name)
        group.permissions.clear()
        self.add_pii_permissions(
            group,
            app_labels=pii_app_labels,
            pii_models=pii_models)

        group_name = 'LAB'
        sys.stdout.write(f' * adding permissions to {group_name}.\n')
        group = Group.objects.get(name=group_name)
        group.permissions.clear()
        self.add_lab_permissions(group)

        group_name = 'PHARMACY'
        sys.stdout.write(f' * adding permissions to {group_name}.\n')
        group = Group.objects.get(name=group_name)
        group.permissions.clear()
        self.add_pharmacy_permissions(group)

    def update_clinic_group_permissions(self, group):
        """Override for custom group permissions.
        """
        pass

    def _update_clinic_group_permissions(self):
        group_name = 'CLINIC'
        sys.stdout.write(f' * adding permissions to {group_name}.\n')
        group = Group.objects.get(name=group_name)
        group.permissions.clear()
        self.update_clinic_group_permissions(group)
        self.add_edc_appointment_permissions(group)
        self.add_edc_action_permissions(group)
        self.remove_historical_permissions(group)
        self.add_navbar_permissions(
            group, codenames=[
                'default_administration', 'edc_lab', 'lab_requisition'])

    def remove_historical_permissions(self, group):
        group.permissions.filter(codename__contains='historical').exclude(
            codename__startswith='view').delete()

    def add_pii_permissions(self, group, view_only=None):
        lookup = dict(
            content_type__app_label__in=self.pii_app_labels,
            content_type__model__in=self.pii_models)
        if view_only:
            lookup.update(codename__startswith='view')
        for permission in Permission.objects.filter(**lookup):
            group.permissions.add(permission)
        for permission in Permission.objects.filter(
                content_type__app_label='edc_registration',
                codename__in=['add_registeredsubject',
                              'delete_registeredsubject',
                              'change_registeredsubject']):
            group.permissions.remove(permission)


class EdcAuthPermissionsUpdaterMixin:

    def add_auth_permissions(self, group):
        for permission in Permission.objects.filter(
                content_type__app_label__in=['auth', 'edc_auth']):
            group.permissions.add(permission)

    def add_userprofile_permissions_to_active(self, group):
        for permission in Permission.objects.filter(
                content_type__app_label='edc_auth',
                content_type__model='userprofile').exclude(
                    codename__in=['add_userprofile', 'delete_userprofile']):
            group.permissions.add(permission)
        for user in User.objects.filter(is_active=True):
            user.groups.add(group)


class EdcPharmacyPermissionsUpdaterMixin:

    def add_pharmacy_permissions(self, group):
        for permission in Permission.objects.filter(content_type__app_label__in=[
                'ambition_pharmacy', 'edc_pharmacy']):
            group.permissions.add(permission)
        self.add_navbar_permissions(
            group, codenames=['default_administration', 'ambition_pharmacy'])


class EdcLabPermissionsUpdaterMixin:

    def add_lab_permissions(self, group):
        for permission in Permission.objects.filter(content_type__app_label='edc_lab'):
            group.permissions.add(permission)
        self.add_navbar_permissions(
            group, codenames=[
                'default_administration', 'ambition_lab', 'lab_requisition', 'lab_receive',
                'lab_process', 'lab_pack', 'lab_manifest', 'lab_aliquot'])


class EdcActionItemPermissionsUpdaterMixin:

    def add_edc_action_permissions(self, group):
        for permission in Permission.objects.filter(
                content_type__app_label='edc_action_item').exclude(
                    codename__in=[
                        'edc_action_item.add_actiontype',
                        'edc_action_item.change_actiontype',
                        'edc_action_item.delete_actiontype']):
            group.permissions.add(permission)


class EdcAppointmentPermissionsUpdaterMixin:

    def add_edc_appointment_permissions(self, group):
        for permission in Permission.objects.filter(
                content_type__app_label='edc_appointment'):
            group.permissions.add(permission)
        permission = Permission.objects.get(
            content_type__app_label='edc_appointment',
            codename='delete_appointment')
        group.permissions.remove(permission)


class EdcNavbarPermissionsUpdaterMixin:

    def add_navbar_permissions(self, group, codenames=None):
        site_navbars.update_permission_codes()
        for codename in codenames:
            permission = Permission.objects.get(
                content_type__app_label='edc_navbar',
                codename=codename)
            group.permissions.add(permission)
