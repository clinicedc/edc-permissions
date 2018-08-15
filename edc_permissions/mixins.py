from django.contrib.auth.models import Permission, User
from edc_navbar.site_navbars import site_navbars


class EdcPermissionsUpdaterMixin:

    def remove_historical_permissions(self, group):
        group.permissions.filter(codename__contains='historical').exclude(
            codename__startswith='view').delete()

    def add_pii_permissions(self, group, app_labels=None, view_only=None):
        app_labels.append('edc_locator')
        app_labels.append('edc_registration')
        app_labels = list(set(app_labels))
        lookup = dict(
            content_type__app_label__in=app_labels,
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
