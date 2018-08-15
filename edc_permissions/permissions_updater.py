import sys

from django.contrib.auth.models import Group, Permission, User
from django.core.exceptions import ObjectDoesNotExist
from edc_navbar.site_navbars import site_navbars


class PermissionsUpdaterError(Exception):
    pass


class PermissionsUpdater:

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
    default_auditor_app_labels = ['edc_lab', 'edc_offstudy']

    auditor_app_labels = None
    group_names = None
    pii_app_labels = None
    pii_models = None

    def __init__(self):
        self.pii_app_labels.extend(self.default_pii_app_labels)
        self.pii_app_labels = list(set(self.pii_app_labels))
        self.pii_models.extend(self.default_pii_models)
        self.pii_models = list(set(self.pii_models))

        self.auditor_app_labels.extend(self.default_auditor_app_labels)
        self.auditor_app_labels = list(set(self.auditor_app_labels))

        self.group_names.extend(self.default_group_names)
        self.group_names = list(set(self.group_names))
        sys.stdout.write('Adding or updating navbar permissions ...\n')
        site_navbars.update_permission_codes()
        sys.stdout.write('Adding or updating groups ...\n')
        self.update_groups()
        sys.stdout.write(
            f"  Groups are: "
            f"{', '.join([obj.name for obj in Group.objects.all().order_by('name')])}\n")
        sys.stdout.write('Adding or updating group permissions ...\n')
        self.update_group_permissions()
        self.remove_historical_permissions()
        sys.stdout.write('Done.\n')

    def extra_auditor_group_permissions(self, group):
        """Override for custom group permissions.
        """
        pass

    def extra_clinic_group_permissions(self, group):
        """Override for custom group permissions.
        """
        pass

    def update_groups(self):
        for name in self.group_names:
            try:
                Group.objects.get(name=name)
            except ObjectDoesNotExist:
                Group.objects.create(name=name)
        Group.objects.exclude(name__in=self.group_names).delete()

    def update_group_permissions(self):
        for group_name in self.default_group_names:
            expression = f'update_{group_name.lower()}_group_permissions'
            sys.stdout.write(f' * adding permissions to group {group_name}.\n')
            exec(f'self.{expression}()')
        for group_name in [n for n in self.group_names if n not in self.default_group_names]:
            expression = f'update_{group_name.lower()}_group_permissions'
            sys.stdout.write(f' * adding permissions to group {group_name}.\n')
            try:
                exec(f'self.{expression}()')
            except AttributeError as e:
                if expression in str(e):
                    raise PermissionsUpdaterError(
                        f'Missing method for group {group_name}. '
                        f'Expected method \'{expression}\'.')
                else:
                    print(expression)
                    raise

    def update_lab_group_permissions(self, group=None):
        if not group:
            group_name = 'LAB'
            group = Group.objects.get(name=group_name)
            group.permissions.clear()
        self.add_lab_permissions(group)

    def update_pharmacy_group_permissions(self, group=None):
        if not group:
            group_name = 'PHARMACY'
            group = Group.objects.get(name=group_name)
            group.permissions.clear()
        self.add_pharmacy_permissions(group)

    def update_pii_group_permissions(self, group=None):
        if not group:
            group_name = 'PII'
            group = Group.objects.get(name=group_name)
            group.permissions.clear()
        self.add_pii_permissions(group)

    def update_everyone_group_permissions(self, group=None):
        if not group:
            group_name = 'EVERYONE'
            group = Group.objects.get(name=group_name)
            group.permissions.clear()
        for permission in Permission.objects.filter(
                content_type__app_label='edc_auth',
                content_type__model='userprofile',
                codename__startswith='view'):
            group.permissions.add(permission)
        for permission in Permission.objects.filter(
                content_type__app_label='auth',
                content_type__model__in=['user', 'group', 'permission'],
                codename__startswith='view'):
            group.permissions.add(permission)
        for permission in Permission.objects.filter(
                content_type__app_label='sites',
                content_type__model='site',
                codename__startswith='view'):
            group.permissions.add(permission)
        for user in User.objects.filter(is_active=True, is_staff=True):
            user.groups.add(group)

    def update_account_manager_group_permissions(self, group=None):
        if not group:
            group_name = 'ACCOUNT_MANAGER'
            group = Group.objects.get(name=group_name)
            group.permissions.clear()
        for permission in Permission.objects.filter(
                content_type__app_label__in=['auth', 'edc_auth']):
            group.permissions.add(permission)

    def update_auditor_group_permissions(self, group=None):
        if not group:
            group_name = 'AUDITOR'
            group = Group.objects.get(name=group_name)
            group.permissions.clear()
        for permission in Permission.objects.filter(
                content_type__app_label__in=self.auditor_app_labels,
                codename__startswith='view'):
            group.permissions.add(permission)
        self.add_edc_action_permissions(group)
        self.add_edc_appointment_permissions(group)
        self.add_pii_permissions(group, view_only=True)
        self.add_navbar_permissions(
            group, codenames=['default_administration', 'lab_section', 'lab_requisition'])
        self.extra_auditor_group_permissions(group)
        for permission in Permission.objects.filter(codename__startswith='change'):
            group.permissions.remove(permission)
        for permission in Permission.objects.filter(codename__startswith='add'):
            group.permissions.remove(permission)
        for permission in Permission.objects.filter(codename__startswith='delete'):
            group.permissions.remove(permission)

    def update_clinic_group_permissions(self, group=None):
        if not group:
            group_name = 'CLINIC'
            group = Group.objects.get(name=group_name)
            group.permissions.clear()
        self.extra_clinic_group_permissions(group)
        self.add_edc_appointment_permissions(group)
        self.add_edc_action_permissions(group)
        self.add_navbar_permissions(
            group, codenames=[
                'default_administration', 'lab_section', 'lab_requisition'])

    def remove_historical_permissions(self):
        for group_name in self.group_names:
            group = Group.objects.get(name=group_name)
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

    def add_navbar_permissions(self, group, codenames=None):
        for codename in codenames:
            permission = Permission.objects.get(
                content_type__app_label='edc_navbar',
                codename=codename)
            group.permissions.add(permission)

    def add_edc_action_permissions(self, group):
        for permission in Permission.objects.filter(
                content_type__app_label='edc_action_item').exclude(
                    codename__in=[
                        'edc_action_item.add_actiontype',
                        'edc_action_item.change_actiontype',
                        'edc_action_item.delete_actiontype']):
            group.permissions.add(permission)

    def add_pharmacy_permissions(self, group):
        for permission in Permission.objects.filter(content_type__app_label__in=[
                'edc_pharmacy', 'edc_pharmacy']):
            group.permissions.add(permission)
        self.add_navbar_permissions(
            group, codenames=['default_administration', 'pharmacy'])

    def add_lab_permissions(self, group):
        for permission in Permission.objects.filter(content_type__app_label='edc_lab'):
            group.permissions.add(permission)
        self.add_navbar_permissions(
            group, codenames=[
                'default_administration', 'lab_section', 'lab_requisition', 'lab_receive',
                'lab_process', 'lab_pack', 'lab_manifest', 'lab_aliquot'])

    def add_edc_appointment_permissions(self, group):
        for permission in Permission.objects.filter(
                content_type__app_label='edc_appointment'):
            group.permissions.add(permission)
        permission = Permission.objects.get(
            content_type__app_label='edc_appointment',
            codename='delete_appointment')
        group.permissions.remove(permission)
