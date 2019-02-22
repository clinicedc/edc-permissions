import django
import sys

from django.apps import apps as django_apps
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from pprint import pprint


def repair_historical_permissions():
    actions = ["add", "change", "delete", "view"]
    if django.VERSION >= (2, 1):
        actions.append("view")
    Permission.objects.filter(codename__contains="historical").delete()
    for app in django_apps.get_app_configs():
        for model in app.get_models():
            try:
                model.history
            except AttributeError:
                pass
            else:
                for action in actions:
                    app_label, model_name = model._meta.label_lower.split(".")
                    content_type = ContentType.objects.get(
                        app_label=app_label, model=model_name
                    )
                    try:
                        perm = Permission.objects.get(
                            content_type=content_type,
                            codename=f"{action}_historical{model_name}",
                        )
                    except ObjectDoesNotExist:
                        Permission.objects.create(
                            content_type=content_type,
                            name=f"Can {action} historical {model._meta.verbose_name}",
                            codename=f"{action}_historical{model_name}",
                        )
                    else:
                        perm.name = (
                            f"Can {action} historical {model._meta.verbose_name}"
                        )
                        perm.save()


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
