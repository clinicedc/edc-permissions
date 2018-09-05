from django.contrib.auth.models import Group

from .constants import DEFAULT_GROUP_NAMES
from django.core.exceptions import ObjectDoesNotExist
from edc_permissions.constants.codenames import DEFAULT_CODENAMES


class PermissionInspectorError(Exception):
    pass


class PermissionsInspector:

    extra_group_names = None

    def __init__(self):
        self.permissions = {}
        self.group_names = [key for key in DEFAULT_GROUP_NAMES]
        self.group_names.extend(self.extra_group_names or [])
        self.group_names = list(set(self.group_names))
        self.group_names.sort()
        groups = Group.objects.filter(name__in=self.group_names)
        for group in groups:
            codenames = [
                p.codename for p in group.permissions.all().order_by('codename')]
            self.permissions.update({group.name: codenames})
        self.validate_default_groups()
        self.validate_default_codenames()

    def get_codenames(self, group_name=None):
        """Returns an ordered list of current codenames from
        Group.permissions for a given group_name.
        """
        if group_name not in self.group_names:
            raise PermissionInspectorError(
                f'Invalid group name. Expected one of {self.group_names}. '
                f'Got {group_name}.')
        codenames = [x for x in self.permissions.get(group_name)]
        codenames.sort()
        return codenames

    def validate_default_groups(self):
        """Raises an exception if a default Edc group does not exist.
        """
        for group_name in DEFAULT_GROUP_NAMES:
            try:
                Group.objects.get(name=group_name)
            except ObjectDoesNotExist:
                raise PermissionInspectorError(
                    f'Default group does not exist. Got {group_name}')

    def validate_default_codenames(self):
        """Raises an exception if a default codename for a
        default Edc group does not exist.
        """
        for group_name, codenames in self.permissions.items():
            for codename in codenames:
                if codename not in DEFAULT_CODENAMES.get(group_name):
                    raise PermissionInspectorError(
                        f'Default codename does not exist for group. '
                        f'Group name is {group_name}. '
                        f'Got {codename}.')
