import sys

from copy import copy
from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.exceptions import MultipleObjectsReturned
from django.core.management.color import color_style
from edc_permissions.constants import DEFAULT_CODENAMES, DEFAULT_PII_MODELS
from edc_permissions.constants import PII, PII_VIEW
from pprint import pprint

from .constants import DEFAULT_GROUP_NAMES

style = color_style()

INVALID_GROUP_NAME = "invalid_group_name"
MISSING_DEFAULT_CODENAME = "missing default codename"
MULTIPLE_CODENAMES = "multiple codenames"
MISSING_DEFAULT_GROUP = "missing default group"
NO_CODENAMES_FOR_GROUP = "no_codenames_for_group"


class PermissionsInspectorError(ValidationError):
    pass


class PermissionsInspectorWarning(ValidationError):
    pass


class PermissionsInspector:
    def __init__(
        self,
        extra_group_names=None,
        extra_pii_models=None,
        manually_validate=None,
        verbose=None,
        default_codenames=None,
        raise_on_warning=None,
    ):
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
                f"{p.content_type.app_label}.{p.codename}"
                for p in group.permissions.all().order_by("codename")
            ]
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
        return django_apps.get_model("auth.group")

    def get_codenames(self, group_name=None):
        """Returns an ordered list of current codenames from
        Group.permissions for a given group_name.
        """
        if group_name not in self.group_names:
            raise PermissionsInspectorError(
                f"Invalid group name. Expected one of {self.group_names}. "
                f"Got {group_name}.",
                code=INVALID_GROUP_NAME,
            )
        if group_name not in self.codenames:
            raise PermissionsInspectorError(
                f"No codenames found for group. See Permissions model. "
                f"Got {group_name}.",
                code=NO_CODENAMES_FOR_GROUP,
            )
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
                    f"Default group does not exist. Got {group_name}",
                    code=MISSING_DEFAULT_GROUP,
                )

    def validate_default_codenames(self):
        """Raises an exception if a default codename list for a
        default Edc group does not exist.

        Permissions codenames in `default_codenames` are of format:
            app_label.codename
        """
        for group_name in self.default_codenames:
            default_codenames = copy(self.default_codenames.get(group_name))
            default_codenames.sort()
            # pprint(default_codenames)
            for default_codename in default_codenames:
                if self.verbose:
                    print(group_name, default_codename)
                app_label, codename = self.get_codename_from(default_codename)
                opts = dict(content_type__app_label=app_label, codename=codename)
                try:
                    self.group_model_cls().objects.get(name=group_name).permissions.get(
                        **opts
                    )
                except ObjectDoesNotExist:
                    raise PermissionsInspectorError(
                        f"Default codename does not exist for group. "
                        f"Group name is {group_name}. "
                        f"Searched group.permissions for {default_codename}. "
                        f"opts={opts}.",
                        code=MISSING_DEFAULT_CODENAME,
                    )
                except MultipleObjectsReturned as e:
                    raise PermissionsInspectorError(
                        f"{e} "
                        f"Group name is {group_name}. "
                        f"Searched group.permissions for {default_codename}.",
                        code=MULTIPLE_CODENAMES,
                    )

    def get_codename_from(self, permissions_codename):
        """Returns the 'codename' part of a permissions codename
        where the format of the given permissions codename
        is `app_label.codename`.

        Some validation checks are done on the permissions_codename
        first.
        """
        try:
            app_label, codename = permissions_codename.split(".")
        except ValueError as e:
            raise PermissionsInspectorError(
                f"Invalid codename. See {permissions_codename}. Got {e}"
            )
        try:
            django_apps.get_app_config(app_label)
        except LookupError:
            sys.stdout.write(
                style.ERROR(
                    f"Invalid codename. '{app_label}' is not a valid App. "
                    f"Got '{permissions_codename}'.\n"
                )
            )
        else:
            if (
                "view" in codename
                or "add" in codename
                or "change" in codename
                or "delete" in codename
            ) and (app_label not in ["edc_dashboard"]):
                model = codename.split("_")[1]
                try:
                    django_apps.get_model(f"{app_label}.{model}")
                except LookupError as e:
                    raise PermissionsInspectorError(
                        f"{e}. See codename='{app_label}.{codename}'."
                    )
        return app_label, codename

    def compare_codenames(self, group_name=None, print_exception=None):
        """For a given group, compare the list of codenames from
        the Permissions model to a default/static list of codenames.
        """
        default_codenames = self.default_codenames.get(group_name)
        if not default_codenames:
            msg = (
                f"Not comparing current codenames to default. "
                f"Group defaults not provided. Got '{group_name}'."
            )
            if self.raise_on_warning:
                raise PermissionsInspectorWarning(msg)
            else:
                sys.stdout.write(style.WARNING(f" * Warning: {msg}\n"))
        else:
            default_codenames.sort()
            actual_codenames = self.get_codenames(group_name)

            if len(actual_codenames) != len(default_codenames):
                sys.stdout.write(
                    style.ERROR(
                        f"Possible duplicate codenames found. See actual codenames "
                        f"for group {group_name}. "
                        f"{len(actual_codenames)}/{len(default_codenames)}\n"
                    )
                )
                print("default_codenames")
                pprint(self.get_duplicates(default_codenames))
                print("actual_codenames")
                pprint(self.get_duplicates(actual_codenames))

            dedup_actual_codenames = self.get_unique_codenames(actual_codenames)
            dedup_default_codenames = self.get_unique_codenames(default_codenames)
            if dedup_default_codenames != dedup_actual_codenames:
                if len(dedup_default_codenames) < len(dedup_actual_codenames):
                    if self.verbose:
                        print("*****default*****")
                        pprint(dedup_default_codenames)
                        print("*****actual*****")
                        pprint(dedup_actual_codenames)
                        print("*****diff default not in actual*****")
                        pprint(
                            [
                                x
                                for x in dedup_default_codenames
                                if x not in dedup_actual_codenames
                            ]
                        )
                        print("*****diff actual not in default*****")
                        pprint(
                            [
                                x
                                for x in dedup_actual_codenames
                                if x not in dedup_default_codenames
                            ]
                        )
                    raise PermissionsInspectorError(
                        f"When comparing Permissions codenames to the default, "
                        f"some codenames are not expected. "
                        f"Got {len(dedup_default_codenames)} defaults != "
                        f"{len(dedup_actual_codenames)} actual. "
                        f"See group {group_name}. (1)"
                    )
                elif len(dedup_default_codenames) > len(dedup_actual_codenames):
                    raise PermissionsInspectorError(
                        f"When comparing Permissions codenames to the default, "
                        "some expected codenames are missing. "
                        f"Got {len(dedup_default_codenames)} defaults != "
                        f"{len(dedup_actual_codenames)} actual. "
                        f"See group {group_name}. (2)"
                    )
                else:
                    error_msg = (
                        f"When comparing Permissions codenames to the default, "
                        f"codenames are incorrect. See group {group_name}. "
                        f"default_codename not in actual_codename: "
                        f"{[x for x in default_codenames if x not in actual_codenames]}. "
                        f"actual_codename not in default_codename: "
                        f"{[x for x in actual_codenames if x not in default_codenames]}. (3)"
                    )
                    if print_exception:
                        sys.stdout.write(style.ERROR(f"{error_msg}\n"))
                    else:
                        raise PermissionsInspectorError(error_msg)

    def get_unique_codenames(self, codenames):
        dedup_codenames = list(set(codenames))
        dedup_codenames.sort()
        return codenames

    def get_duplicates(self, codenames):
        return list(set([x for x in codenames if codenames.count(x) > 1]))

    def diff_codenames(self, group_name=None):
        """Returns a dictionary of unexpected and missing codenames.

        For example:

            # import your codenames and group_names
            default_codenames=default_codenames
            extra_group_names

            from ambition_auth.codenames import CODENAMES
            from ambition_auth.group_names import TMG
            from edc_permissions.constants import AUDITOR
            from edc_permissions.permissions_inspector import PermissionsInspector

            inspector = PermissionsInspector(
                manually_validate=True,
                default_codenames=CODENAMES,
                extra_group_names=[TMG])
            inspector.diff_codenames(group_name=AUDITOR)

        """
        defaults = self.default_codenames.get(group_name)
        existing = [x for x in self.get_codenames(group_name)]
        return {
            "unexpected": [x for x in existing if x not in defaults],
            "missing": [x for x in defaults if x not in existing],
        }

    def remove_codenames(self, group_name=None, codenames=None):
        """Remove persisted codenames.

        For example:
            inspector.remove_codenames(
                group_name=AUDITOR,
                codenames=['view_action', 'add_action',
                           'delete_action', 'change_action'])
        """
        group = self.group_model_cls().objects.get(name=group_name)
        deleted = group.permissions.filter(
            group__name=group_name, codename__in=codenames
        ).delete()
        return deleted

    def validate_pii(self):
        """Ensure PII codenames not in any other group.
        """
        for group_name in self.group_names:
            if group_name not in [PII, PII_VIEW]:
                group = self.group_model_cls().objects.get(name=group_name)
                codenames = [
                    x.codename for x in group.permissions.filter(group__name=group_name)
                ]
                deleted = group.permissions.filter(
                    group__name=group_name,
                    codename__in=[x for x in codenames if x in PII],
                ).delete()
                if deleted[0]:
                    raise PermissionsInspectorWarning(
                        f"Group unexpectedly permits PII codenames. Got {deleted}. "
                        f"See group_name {group_name}."
                    )
