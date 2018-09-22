from copy import copy
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from edc_permissions.constants import DEFAULT_CODENAMES, DEFAULT_PII_MODELS

from .constants import DEFAULT_GROUP_NAMES

INVALID_GROUP_NAME = 'invalid_group_name'
MISSING_DEFAULT_CODENAME = 'missing default codename'
MISSING_DEFAULT_GROUP = 'missing default group'


class PermissionsInspectorError(ValidationError):
    pass


class PermissionsInspector:

    def __init__(self, extra_group_names=None, extra_pii_models=None,
                 manually_validate=None, verbose=None):
        self.permissions = {}
        self.verbose = verbose

        self.group_names = [key for key in DEFAULT_GROUP_NAMES]
        self.group_names.extend(extra_group_names or [])
        self.group_names = list(set(self.group_names))
        self.group_names.sort()

        groups = Group.objects.filter(name__in=self.group_names)
        for group in groups:
            codenames = [
                p.codename for p in group.permissions.all().order_by('codename')]
            self.permissions.update({group.name: codenames})

        self.pii_models = copy(DEFAULT_PII_MODELS)
        self.pii_models.extend(extra_pii_models or [])
        self.pii_models = list(set(self.pii_models))
        self.pii_models.sort()

        if not manually_validate:
            self.validate_default_groups()
            self.validate_default_codenames()

    def get_codenames(self, group_name=None):
        """Returns an ordered list of current codenames from
        Group.permissions for a given group_name.
        """
        if group_name not in self.group_names:
            raise PermissionsInspectorError(
                f'Invalid group name. Expected one of {self.group_names}. '
                f'Got {group_name}.', code=INVALID_GROUP_NAME)
        codenames = [x for x in self.permissions.get(group_name)]
        codenames.sort()
        return codenames

    def validate_default_groups(self):
        """Raises an exception if a default Edc group does not exist.
        """
        for group_name in DEFAULT_GROUP_NAMES:
            if self.verbose:
                print(group_name)
            try:
                Group.objects.get(name=group_name)
            except ObjectDoesNotExist:
                raise PermissionsInspectorError(
                    f'Default group does not exist. Got {group_name}',
                    code=MISSING_DEFAULT_GROUP)

    def validate_default_codenames(self):
        """Raises an exception if a default codename for a
        default Edc group does not exist.
        """
        for group_name in DEFAULT_GROUP_NAMES:
            default_codenames = copy(DEFAULT_CODENAMES.get(group_name))
            default_codenames.sort()
            for default_codename in default_codenames:
                if self.verbose:
                    print(group_name, default_codename)
                try:
                    Group.objects.get(name=group_name).permissions.get(
                        codename=default_codename)
                except ObjectDoesNotExist:
                    raise PermissionsInspectorError(
                        f'Default codename does not exist for group. '
                        f'Group name is {group_name}. '
                        f'Expected codenames are {default_codenames}. '
                        f'Searched group.permissions for {default_codename}.',
                        code=MISSING_DEFAULT_CODENAME)
