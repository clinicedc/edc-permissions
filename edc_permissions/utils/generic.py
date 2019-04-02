import sys

from django.apps import apps as django_apps
from django.contrib.auth.models import Group, Permission
from pprint import pprint
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from ..pii_updater import PiiUpdater

INVALID_APP_LABEL = "invalid_app_label"


class CodenameDoesNotExist(Exception):
    pass


class PermissionsCodenameError(Exception):
    pass


class PermissionsCreatorError(ValidationError):
    pass


def add_permissions_to_group_by_model(group_name=None, model_cls=None):
    try:
        group = Group.objects.get(name=group_name)
    except ObjectDoesNotExist as e:
        raise ObjectDoesNotExist(f"{e} Got {group_name}.")
    ct = ContentType.objects.get_for_model(model_cls)
    for permission in Permission.objects.filter(content_type=ct):
        group.permissions.add(permission)


def add_permissions_to_group_by_app_label(group=None, app_label=None):
    for permission in Permission.objects.filter(content_type__app_label=app_label):
        group.permissions.add(permission)


def add_permissions_to_group_by_codenames(group=None, codenames=None):
    if codenames:
        for codename in codenames:
            verify_codename_exists(codename)
        for permission in Permission.objects.filter(codename__in=codenames):
            group.permissions.add(permission)


def add_permissions_to_group_by_tuples(group=None, codename_tpls=None):
    codenames = []
    for codename_tpl in codename_tpls or []:
        _, codename, _ = get_from_codename_tuple(codename_tpl)
        verify_codename_exists(codename)
        codenames.append(codename)
    for permission in Permission.objects.filter(codename__in=codenames):
        group.permissions.add(permission)


def as_codenames_from_dict(dct):
    codenames = []
    for codename_tpls in dct.values():
        codenames.extend(as_codenames_from_tuples(codename_tpls))
    return codenames


def as_codenames_from_tuples(codename_tpls):
    codenames = []
    for codename_tpl in codename_tpls:
        try:
            _, codename = codename_tpl[0]
        except ValueError:
            codename = codename_tpl[0]
        codenames.append(codename)
    return codenames


def compare_codenames_for_group(group_name=None, expected=None):
    group = Group.objects.get(name=group_name)
    codenames = [p.codename for p in group.permissions.all()]

    new_expected = []
    for c in expected:
        try:
            c = c.split(".")[1]
        except IndexError:
            pass
        new_expected.append(c)

    compared = [c for c in new_expected if c not in codenames]
    if compared:
        print(group.name, "missing from codenames")
        pprint(compared)
    compared = [c for c in codenames if c not in new_expected]
    if compared:
        print(group.name, "extra codenames")
        pprint(compared)


def create_permissions_from_tuples(model, codename_tpls):
    """Creates custom permissions on "model".
    """
    if codename_tpls:
        model_cls = django_apps.get_model(model)
        content_type = ContentType.objects.get_for_model(model_cls)
        for codename_tpl in codename_tpls:
            _, codename, name = get_from_codename_tuple(
                codename_tpl, model_cls._meta.app_label
            )
            try:
                Permission.objects.get(codename=codename, content_type=content_type)
            except ObjectDoesNotExist:
                Permission.objects.create(
                    name=name, codename=codename, content_type=content_type
                )


def get_from_codename_tuple(codename_tpl, app_label=None):
    value, name = codename_tpl
    try:
        _app_label, codename = value.split(".")
    except ValueError:
        _app_label, codename = app_label, value
    else:
        if app_label and _app_label != app_label:
            raise PermissionsCreatorError(
                f"app_label in permission codename does not match. "
                f"Expected {app_label}. Got {_app_label}. "
                f"See {codename_tpl}.",
                code=INVALID_APP_LABEL,
            )
    return app_label, codename, name


def get_from_dotted_codename(codename=None, default_app_label=None, **kwargs):
    if not codename:
        raise PermissionsCodenameError(
            f"Invalid codename. May not be None. Opts={kwargs}."
        )
    try:
        app_label, _codename = codename.split(".")
    except ValueError as e:
        if not default_app_label:
            raise PermissionsCodenameError(
                f"Invalid dotted codename. {e} Got {codename}."
            )
        app_label = default_app_label
        _codename = codename
    else:
        if app_label not in [a.name for a in django_apps.get_app_configs()]:
            raise PermissionsCodenameError(
                f"Invalid app_label in codename. Expected format "
                f"'<app_label>.<some_codename>'. Got {codename}."
            )
    return app_label, _codename


def make_view_only_group(group=None):
    for permission in Permission.objects.filter(codename__startswith="change"):
        group.permissions.remove(permission)
    for permission in Permission.objects.filter(codename__startswith="add"):
        group.permissions.remove(permission)
    for permission in Permission.objects.filter(codename__startswith="delete"):
        group.permissions.remove(permission)


def make_view_only_app_label(group=None, app_label=None):
    for permission in Permission.objects.filter(
        codename__startswith="change", content_type__app_label=app_label
    ):
        group.permissions.remove(permission)
    for permission in Permission.objects.filter(
        codename__startswith="add", content_type__app_label=app_label
    ):
        group.permissions.remove(permission)
    for permission in Permission.objects.filter(
        codename__startswith="delete", content_type__app_label=app_label
    ):
        group.permissions.remove(permission)


def make_view_only_model(group=None, model=None):
    model_cls = django_apps.get_model(model)
    content_type = ContentType.objects.get_for_model(model_cls)
    for permission in Permission.objects.filter(
        codename__startswith="change", content_type=content_type
    ):
        group.permissions.remove(permission)
    for permission in Permission.objects.filter(
        codename__startswith="add", content_type=content_type
    ):
        group.permissions.remove(permission)
    for permission in Permission.objects.filter(
        codename__startswith="delete", content_type=content_type
    ):
        group.permissions.remove(permission)


def remove_historical_group_permissions(group=None, allowed_permissions=None):
    """Removes group permissions for historical models
    except those whose prefix is in `allowed_historical_permissions`.

    Default removes all except `view`.
    """
    allowed_permissions = allowed_permissions or ["view"]

    for action in allowed_permissions:
        for permission in group.permissions.filter(
            codename__contains="historical"
        ).exclude(codename__startswith=action):
            group.permissions.remove(permission)


def remove_duplicates_in_groups(group_names):
    for group_name in group_names:
        group = Group.objects.get(name=group_name)
        for i in [0, 1]:
            codenames = [
                f"{x.content_type.app_label}.{x.codename}"
                for x in group.permissions.all().order_by(
                    "content_type__app_label", "codename"
                )
            ]
            duplicates = list(set([x for x in codenames if codenames.count(x) > 1]))
            if duplicates:
                if i > 0:
                    sys.stdout.write(
                        f"  ! Duplicate permissions found for group {group_name}.\n"
                        f"  !   duplicates will be removed, but you should rerun the \n"
                        f"  !   permissions updater ({len(duplicates)}/{len(codenames)})."
                    )
                    pprint(duplicates)
                for duplicate in duplicates:
                    app_label, codename = duplicate.split(".")
                    for permission in group.permissions.filter(
                        content_type__app_label=app_label, codename=codename
                    ):
                        group.permissions.remove(permission)
                    group.permissions.add(permission)


def get_pii_models(extra_pii_models=None):
    pii = PiiUpdater(extra_pii_models=extra_pii_models, no_update=True)
    return pii.pii_models


def remove_pii_permissions_from_group(group, extra_pii_models=None):
    pii = PiiUpdater(extra_pii_models=extra_pii_models, no_update=True)
    for model in pii.pii_models:
        remove_permissions_by_model(group, model)


def remove_permissions_from_model_by_action(group=None, model=None, actions=None):
    model_cls = django_apps.get_model(model)
    content_type = ContentType.objects.get_for_model(model_cls)
    for action in actions:
        for permission in Permission.objects.filter(
            content_type=content_type, codename_startswith=action
        ):
            group.permissions.remove(permission)


def remove_permissions_by_codenames(group=None, codenames=None):
    for permission in Permission.objects.filter(codename__in=codenames):
        group.permissions.remove(permission)


def remove_permissions_by_model(group=None, model=None):
    model_cls = django_apps.get_model(model)
    content_type = ContentType.objects.get_for_model(model_cls)
    for permission in Permission.objects.filter(content_type=content_type):
        group.permissions.remove(permission)


def show_permissions_for_group(group_name=None):
    group = Group.objects.get(name=group_name)
    print(group.name)
    pprint([p for p in group.permissions.all()])


def verify_codename_exists(codename):
    try:
        permission = Permission.objects.get(codename=codename)
    except ObjectDoesNotExist as e:
        raise CodenameDoesNotExist(f"{e} Got '{codename}'")
    return permission