import sys

from copy import copy
from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.management.color import color_style
from edc_permissions.constants import DEFAULT_CODENAMES, DEFAULT_PII_MODELS
from edc_permissions.constants import PII, PII_VIEW

from .constants import DEFAULT_GROUP_NAMES

style = color_style()

INVALID_GROUP_NAME = 'invalid_group_name'
MISSING_DEFAULT_CODENAME = 'missing default codename'
MISSING_DEFAULT_GROUP = 'missing default group'
NO_CODENAMES_FOR_GROUP = 'no_codenames_for_group'


class PermissionsInspectorError(ValidationError):
    pass


class PermissionsInspectorWarning(ValidationError):
    pass


class PermissionsInspector:

    def __init__(self, extra_group_names=None, extra_pii_models=None,
                 manually_validate=None, verbose=None, default_codenames=None,
                 raise_on_warning=None):
        self.codenames = {}
        self.verbose = verbose
        self.default_codenames = default_codenames or DEFAULT_CODENAMES
        self.default_codenames.update(**default_codenames or {})
        self.raise_on_warning = raise_on_warning

        self.group_names = [key for key in DEFAULT_GROUP_NAMES]
        self.group_names.extend(extra_group_names or [])
        self.group_names = list(set(self.group_names))
        self.group_names.sort()

        groups = self.group_model_cls().objects.filter(name__in=self.group_names)
        for group in groups:
            codenames = [
                p.codename for p in group.permissions.all().order_by('codename')]
            self.codenames.update({group.name: codenames})

        self.pii_models = copy(DEFAULT_PII_MODELS)
        self.pii_models.extend(extra_pii_models or [])
        self.pii_models = list(set(self.pii_models))
        self.pii_models.sort()

        if not manually_validate:
            self.validate_default_groups()
            self.validate_default_codenames()
            for group_name in self.group_names:
                self.compare_codenames(group_name=group_name)

    def group_model_cls(self):
        return django_apps.get_model('auth.group')

    def get_codenames(self, group_name=None):
        """Returns an ordered list of current codenames from
        Group.permissions for a given group_name.
        """
        if group_name not in self.group_names:
            raise PermissionsInspectorError(
                f'Invalid group name. Expected one of {self.group_names}. '
                f'Got {group_name}.', code=INVALID_GROUP_NAME)
        if group_name not in self.codenames:
            raise PermissionsInspectorError(
                f'No codenames found for group. See Permissions model. '
                f'Got {group_name}.', code=NO_CODENAMES_FOR_GROUP)
        codenames = [x for x in self.codenames.get(group_name)]
        codenames.sort()
        return codenames

    def validate_default_groups(self):
        """Raises an exception if a default Edc group does not exist.
        """
        for group_name in DEFAULT_GROUP_NAMES:
            if self.verbose:
                print(group_name)
            try:
                self.group_model_cls().objects.get(name=group_name)
            except ObjectDoesNotExist:
                raise PermissionsInspectorError(
                    f'Default group does not exist. Got {group_name}',
                    code=MISSING_DEFAULT_GROUP)

    def validate_default_codenames(self):
        """Raises an exception if a default codename list for a
        default Edc group does not exist.
        """
        for group_name in self.default_codenames:
            default_codenames = copy(self.default_codenames.get(group_name))
            default_codenames.sort()
            for default_codename in default_codenames:
                if self.verbose:
                    print(group_name, default_codename)
                try:
                    self.group_model_cls().objects.get(name=group_name).permissions.get(
                        codename=default_codename)
                except ObjectDoesNotExist:
                    raise PermissionsInspectorError(
                        f'Default codename does not exist for group. '
                        f'Group name is {group_name}. '
                        f'Expected codenames are {default_codenames}. '
                        f'Searched group.permissions for {default_codename}.',
                        code=MISSING_DEFAULT_CODENAME)

    def compare_codenames(self, group_name):
        """For a given group, compare the list of codenames from
        the Permissions model to a default/static list of codenames.
        """
        default_codenames = self.default_codenames.get(group_name)
        if not default_codenames:
            msg = (f'Not comparing current codenames to default. '
                   f'Group defaults not provided. Got \'{group_name}\'.')
            if self.raise_on_warning:
                raise PermissionsInspectorWarning(msg)
            else:
                sys.stdout.write(style.WARNING(f' * Warning: {msg}\n'))
        else:
            default_codenames.sort()
            if default_codenames != self.get_codenames(group_name):
                if len(default_codenames) < len(self.get_codenames(group_name)):
                    raise PermissionsInspectorError(
                        f'When comparing Permissions codenames to the default, '
                        f'some codenames are not expected. '
                        f'Got {len(default_codenames)} defaults != '
                        f'{len(self.get_codenames(group_name))} actual. '
                        f'See group {group_name}.')
                elif len(default_codenames) > len(self.get_codenames(group_name)):
                    raise PermissionsInspectorError(
                        f'When comparing Permissions codenames to the default, '
                        'some expected codenames are missing. '
                        f'Got {len(default_codenames)} defaults != '
                        f'{len(self.get_codenames(group_name))} actual. '
                        f'See group {group_name}.')
                else:
                    raise PermissionsInspectorError(
                        f'When comparing Permissions codenames to the default, '
                        f'codenames are incorrect. See group {group_name}.')

    def diff_codenames(self, group_name=None):
        """Returns a dictionary of unexpected and missing codenames.

        For example:

            # import your codenames and group_names
            default_codenames=default_codenames
            extra_group_names

            from edc_permissions.constants import AUDITOR
            from edc_permissions.permissions_inspector import PermissionsInspector

            inspector = PermissionsInspector(
                manually_validate=True,
                default_codenames=default_codenames,
                extra_group_names=extra_group_names)
            inspector.diff_codenames(group_name=AUDITOR)

        """
        defaults = self.default_codenames.get(group_name)
        existing = [x for x in self.get_codenames(group_name)]
        return {'unexpected': [x for x in existing if x not in defaults],
                'missing': [x for x in defaults if x not in existing]}

    def remove_codenames(self, group_name=None, codenames=None):
        group = self.group_model_cls().objects.get(name=group_name)
        deleted = group.permissions.filter(
            group__name=group_name, codename__in=codenames).delete()
        return deleted

    def validate_pii(self):
        """Ensure PII codenames not in any other group.
        """
        for group_name in self.group_names:
            if group_name not in [PII, PII_VIEW]:
                group = self.group_model_cls().objects.get(name=group_name)
                codenames = [x.codename for x in group.permissions.filter(
                    group__name=group_name)]
                deleted = group.permissions.filter(
                    group__name=group_name, codename__in=[
                        x for x in codenames if x in PII]).delete()
                if deleted[0]:
                    raise PermissionsInspectorWarning(
                        f'Group unexpectedly permits PII codenames. Got {deleted}. '
                        f'See group_name {group_name}.')
