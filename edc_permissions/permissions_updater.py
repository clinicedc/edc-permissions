import sys

from copy import copy
from django.apps import apps as django_apps
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Q
from edc_navbar.site_navbars import site_navbars

from .constants import (
    ACCOUNT_MANAGER, ADMINISTRATION, EXPORT,
    EVERYONE, AUDITOR, CLINIC, LAB, PHARMACY, PII, PII_VIEW,
    DEFAULT_GROUP_NAMES, DEFAULT_PII_MODELS,
    DEFAULT_AUDITOR_APP_LABELS, LAB_DASHBOARD_CODENAMES)


DUPLICATE_CODENAME = 'duplicate_codename'


class PermissionsUpdaterError(ValidationError):
    pass


class PermissionsUpdater:

    """
    A class to setup default model, navbar and dashboard permissions
    for each of the default groups.

    Each group has a custom update method of the format
    `update_xxx_group_permissions` where xxx is the group name.

    If code is called by multiple custom `update_xxx ...` methods
    it may be put in a custom `add_xxx_permissions` method where xxx
    can be a group name or some other unique string.

    `extra_...` attributes are either set or overridden but the
    user.
    """

    default_group_names = DEFAULT_GROUP_NAMES
    default_pii_models = DEFAULT_PII_MODELS
    default_auditor_app_labels = DEFAULT_AUDITOR_APP_LABELS
    default_dashboard_codenames = {
        LAB: LAB_DASHBOARD_CODENAMES}

    navbar_codenames = {
        ADMINISTRATION: ['nav_administration'],
        AUDITOR: ['nav_lab_section', 'nav_lab_requisition'],
        CLINIC: ['nav_lab_section', 'nav_lab_requisition'],
        LAB: ['nav_lab_section', 'nav_lab_requisition',
              'nav_lab_receive', 'nav_lab_process',
              'nav_lab_pack', 'nav_lab_manifest',
              'nav_lab_aliquot'],
        PHARMACY: ['nav_pharmacy_section'],
    }

    extra_auditor_app_labels = None
    extra_dashboard_codenames = None
    extra_group_names = None
    extra_pii_models = None

    def __init__(self, verbose=None):

        self.dashboard_codenames = copy(self.default_dashboard_codenames)
        if self.extra_dashboard_codenames:
            self.dashboard_codenames.update(**self.extra_dashboard_codenames)

        self.write = str if verbose is False else sys.stdout.write

        self.pii_models = copy(self.default_pii_models or [])
        if self.extra_pii_models:
            self.pii_models.extend(self.extra_pii_models or [])
        self.pii_models = list(set(self.pii_models))
        self.pii_models.sort()

        self.auditor_app_labels = copy(self.default_auditor_app_labels or [])
        if self.extra_auditor_app_labels:
            self.auditor_app_labels.extend(self.extra_auditor_app_labels or [])
        self.auditor_app_labels = list(set(self.auditor_app_labels))
        self.auditor_app_labels.sort()

        self.group_names = copy(self.default_group_names or [])
        if self.extra_group_names:
            self.group_names.extend(self.extra_group_names or [])
        self.group_names = list(set(self.group_names))
        self.group_names.sort()

        self.check_app_labels()

        self.write('Adding or updating navbar permissions ...\n')
        site_navbars.update_permission_codenames(verbose=False)

        self.write('Adding or updating dashboard permissions ...\n')
        self.update_dashboard_codenames()

        self.write('Adding or updating groups ...\n')
        self.update_groups()
        self.write(
            f"  Groups are: "
            f"{', '.join([obj.name for obj in Group.objects.all().order_by('name')])}\n")
        self.write('Adding or updating group permissions ...\n')
        self.update_group_permissions()
        self.remove_historical_permissions()  # if not view
        self.write('Done.\n')

    def extra_auditor_group_permissions(self, group):
        """Override for custom group permissions.
        """
        pass

    def extra_export_group_permissions(self, group):
        """Override for custom group permissions.
        """
        pass

    def extra_clinic_group_permissions(self, group):
        """Override for custom group permissions.
        """
        pass

    def extra_lab_group_permissions(self, group):
        """Override for custom group permissions.
        """
        pass

    def extra_pharmacy_group_permissions(self, group):
        """Override for custom group permissions.
        """
        pass

    def update_groups(self):
        """Add/Deletes group model instances to match the
        the given list of group names.
        """
        for name in self.group_names:
            try:
                Group.objects.get(name=name)
            except ObjectDoesNotExist:
                Group.objects.create(name=name)
        Group.objects.exclude(name__in=self.group_names).delete()

    def update_group_permissions(self):
        """Calls the `update_xxxx_group_permissions` method
        for each group name.

        Permissions are model-based so be sure to add the APP
        to INSTALLED_APPS.
        """
        for group_name in self.default_group_names:
            expression = f'update_{group_name.lower()}_group_permissions'
            self.write(f' * adding permissions to group {group_name}.\n')
            exec(f'self.{expression}()')
        for group_name in [n for n in self.group_names
                           if n not in self.default_group_names]:
            expression = f'update_{group_name.lower()}_group_permissions'
            self.write(f' * adding permissions to group {group_name}.\n')
            try:
                exec(f'self.{expression}()')
            except AttributeError as e:
                if expression in str(e):
                    raise PermissionsUpdaterError(
                        f'Missing method for group {group_name}. '
                        f'Expected method \'{expression}\'.',
                        code='missing_method')
                else:
                    print(expression)
                    raise

    def add_navbar_permissions(self, group, codenames=None):
        """Adds the navbar permissions from edc_navbar.
        """
        self.add_permissions(
            group=group, app_label='edc_navbar', codenames=codenames,
            exception_code='missing_navbar_codename')

    def add_permissions(self, group=None, app_label=None, model=None,
                        codenames=None, exception_code=None):
        """Adds a permission to a group for the given criteria.
        """
        opts = {}
        exception_code = exception_code or 'missing_codename'
        if app_label:
            opts.update({'content_type__app_label': app_label})
        if model:
            opts.update({'content_type__model': model})
        for codename in codenames:
            opts.update(codename=codename)
            try:
                permission = Permission.objects.get(**opts)
            except ObjectDoesNotExist as e:
                raise PermissionsUpdaterError(
                    f'{e}. Got {codename}', code=exception_code)
            else:
                group.permissions.add(permission)

    def check_app_labels(self):
        pii_app_labels = [m.split('.')[0] for m in self.pii_models]
        for app_labels in [self.auditor_app_labels, pii_app_labels]:
            for app_label in app_labels:
                try:
                    django_apps.get_app_config(app_label)
                except LookupError as e:
                    raise PermissionsUpdaterError(e, code='lookup')

    def remove_historical_permissions(self):
        """Removes all permissions for historical models
        except `view`.
        """
        for group_name in self.group_names:
            group = Group.objects.get(name=group_name)
            group.permissions.filter(codename__contains='historical').exclude(
                codename__startswith='view').delete()

    def add_dashboard_permissions(self, group, dashboard_category=None, codename=None):
        """Adds dashboard permissions linked to edc_dashboard
        either by category or single codename.
        """
        codenames = []
        if codename:
            codenames.append(codename)
        if dashboard_category:
            codenames.extend(
                [c[0] for c in self.dashboard_codenames[dashboard_category]])
        for codename in codenames:
            try:
                permission = Permission.objects.get(
                    content_type__app_label='edc_dashboard',
                    codename=codename)
            except ObjectDoesNotExist:
                raise PermissionsUpdaterError(
                    f'Permission does not exist for codename. Got {codename}')
            group.permissions.add(permission)

    def update_dashboard_codenames(self):
        """Creates or updates Permissions for dashboard codenames
        associated with edc_dashboard.Dashboard.

        Adds extra codenames and assert no duplicates.
        """
        codenames = []
        for values in self.dashboard_codenames.values():
            codenames.extend([v[0] for v in values])
        deduped = list(set(codenames))
        deduped.sort()
        codenames.sort()
        if deduped != codenames:
            raise PermissionsUpdaterError(
                f'Duplicate dashboard codenames detected. '
                f'Got {codenames}.', code=DUPLICATE_CODENAME)
        for codenames in self.dashboard_codenames.values():
            for codename in codenames:
                self.get_or_create_dashboard_permission(codename)

    def get_or_create_dashboard_permission(self, codename):
        """Get or create permissions for dashboards and listboards.

        Permissions are attached to edc_dashboard.Dashboard.
        """
        content_type = ContentType.objects.get(
            app_label='edc_dashboard',
            model='dashboard')
        try:
            permission = Permission.objects.get(
                content_type=content_type,
                codename=codename[0],
                name=codename[1])
        except ObjectDoesNotExist:
            Permission.objects.filter(
                content_type=content_type,
                codename=codename[1]).delete()
            permission = Permission.objects.create(
                content_type=content_type,
                codename=codename[0],
                name=codename[1])
        return permission

    def ensure_users_in_group(self, group_name, users_by_groups=None):
        group = Group.objects.get(name=group_name)
        for user in User.objects.filter(groups__name__in=users_by_groups):
            try:
                user.groups.get(name=group.name)
            except ObjectDoesNotExist:
                user.groups.add(group)

    def ensure_users_not_in_group(self, group_name, users_by_groups=None):
        group = Group.objects.get(name=group_name)
        for user in User.objects.filter(groups__name__in=users_by_groups):
            try:
                user.groups.get(name=group.name)
            except ObjectDoesNotExist:
                pass
            else:
                user.groups.remove(group)

    def update_export_group_permissions(self):
        group_name = EXPORT
        group = Group.objects.get(name=group_name)
        group.permissions.clear()
        for permission in Permission.objects.filter(
                content_type__app_label='edc_export'):
            group.permissions.add(permission)
        self.extra_export_group_permissions(group)

    def update_lab_group_permissions(self):
        group_name = LAB
        group = Group.objects.get(name=group_name)
        group.permissions.clear()
        self.add_lab_permissions(group)
        self.add_dashboard_permissions(group, dashboard_category=LAB)
        self.extra_lab_group_permissions(group)

    def update_pharmacy_group_permissions(self):
        group_name = PHARMACY
        group = Group.objects.get(name=group_name)
        group.permissions.clear()
        self.extra_pharmacy_group_permissions(group)
        # add model permissions
        for permission in Permission.objects.filter(
                content_type__app_label='edc_pharmacy'):
            group.permissions.add(permission)
        self.add_navbar_permissions(
            group, codenames=self.navbar_codenames.get(PHARMACY))

    def update_pii_group_permissions(self):
        group_name = PII
        group = Group.objects.get(name=group_name)
        group.permissions.clear()
        self.add_pii_permissions(group)

    def update_pii_view_group_permissions(self):
        group_name = PII_VIEW
        group = Group.objects.get(name=group_name)
        group.permissions.clear()
        self.add_pii_permissions(group, view_only=True)

    def update_everyone_group_permissions(self):
        group_name = EVERYONE
        group = Group.objects.get(name=group_name)
        group.permissions.clear()
        for permission in Permission.objects.filter(
                content_type__app_label='edc_auth',
                content_type__model='userprofile',
                codename__in=['view_userprofile']):
            group.permissions.add(permission)
        for permission in Permission.objects.filter(
                content_type__app_label='auth',
                content_type__model__in=[
                    'user', 'group', 'permission'],
                codename__startswith='view'):
            group.permissions.add(permission)
        for permission in Permission.objects.filter(
                content_type__app_label='sites',
                content_type__model='site',
                codename__startswith='view'):
            group.permissions.add(permission)
        for permission in Permission.objects.filter(
                content_type__app_label='admin',
                codename__startswith='view'):
            group.permissions.add(permission)
        for user in User.objects.filter(is_active=True, is_staff=True):
            user.groups.add(group)

    def update_account_manager_group_permissions(self):
        group_name = ACCOUNT_MANAGER
        group = Group.objects.get(name=group_name)
        group.permissions.clear()
        for permission in Permission.objects.filter(
                content_type__app_label__in=['auth', 'edc_auth']):
            group.permissions.add(permission)

    def update_auditor_group_permissions(self):
        group_name = AUDITOR
        group = Group.objects.get(name=group_name)
        group.permissions.clear()
        self.extra_auditor_group_permissions(group)
        for permission in Permission.objects.filter(
                content_type__app_label__in=self.auditor_app_labels,
                codename__startswith='view'):
            group.permissions.add(permission)
        self.add_edc_action_permissions(group)
        self.add_edc_appointment_permissions(group)
        self.add_navbar_permissions(
            group, codenames=self.navbar_codenames.get(AUDITOR))
        for permission in Permission.objects.filter(codename__startswith='change'):
            group.permissions.remove(permission)
        for permission in Permission.objects.filter(codename__startswith='add'):
            group.permissions.remove(permission)
        for permission in Permission.objects.filter(codename__startswith='delete'):
            group.permissions.remove(permission)
        self.add_dashboard_permissions(
            group, codename='view_lab_requisition_listboard')

    def update_clinic_group_permissions(self):
        group_name = CLINIC
        group = Group.objects.get(name=group_name)
        group.permissions.clear()
        self.extra_clinic_group_permissions(group)
        self.add_edc_appointment_permissions(group)
        self.add_edc_offstudy_permissions(group)
        self.add_edc_action_permissions(group)
        self.add_navbar_permissions(
            group, codenames=self.navbar_codenames.get(CLINIC))
        self.add_dashboard_permissions(
            group, codename='view_lab_requisition_listboard')

    def update_administration_group_permissions(self):
        group_name = ADMINISTRATION
        group = Group.objects.get(name=group_name)
        group.permissions.clear()
        self.add_navbar_permissions(
            group, codenames=self.navbar_codenames.get(ADMINISTRATION))

    def add_pii_permissions(self, group, view_only=None):
        """Adds PII model permissions.
        """
        pii_model_names = [m.split('.')[1] for m in self.pii_models]
        if view_only:
            permissions = Permission.objects.filter(
                (Q(codename__startswith='view') | Q(
                    codename__startswith='display')),
                content_type__model__in=pii_model_names)
        else:
            permissions = Permission.objects.filter(
                content_type__model__in=pii_model_names)
        for permission in permissions:
            group.permissions.add(permission)
        for permission in Permission.objects.filter(
                content_type__app_label='edc_registration',
                codename__in=['add_registeredsubject',
                              'delete_registeredsubject',
                              'change_registeredsubject']):
            group.permissions.remove(permission)

    def add_edc_action_permissions(self, group):
        for permission in Permission.objects.filter(
                content_type__app_label='edc_action_item').exclude(
                    codename__in=[
                        'edc_action_item.add_actiontype',
                        'edc_action_item.change_actiontype',
                        'edc_action_item.delete_actiontype']):
            group.permissions.add(permission)

    def add_lab_permissions(self, group):
        for permission in Permission.objects.filter(
                content_type__app_label='edc_lab'):
            group.permissions.add(permission)
        self.add_navbar_permissions(
            group, codenames=self.navbar_codenames.get(LAB))

    def add_edc_appointment_permissions(self, group):
        for permission in Permission.objects.filter(
                content_type__app_label='edc_appointment'):
            group.permissions.add(permission)
        permission = Permission.objects.get(
            content_type__app_label='edc_appointment',
            codename='delete_appointment')
        group.permissions.remove(permission)

    def add_edc_offstudy_permissions(self, group):
        for permission in Permission.objects.filter(
                content_type__app_label='edc_offstudy'):
            group.permissions.add(permission)
