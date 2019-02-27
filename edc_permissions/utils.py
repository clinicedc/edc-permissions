import django
import sys

from django.apps import apps as django_apps
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from pprint import pprint


def reset_historical_model_codenames(dry_run=None, clear_existing=None):
    """Ensures all historical model codenames exist in Django's Permission
    model.
    """
    created_codenames = []
    updated_names = []
    actions = ["add", "change", "delete", "view"]
    if django.VERSION >= (2, 1):
        actions.append("view")
    for app in django_apps.get_app_configs():
        for model in app.get_models():
            try:
                manager = getattr(model, model._meta.simple_history_manager_attribute)
            except AttributeError:
                pass
            else:
                historical_model = manager.model
                app_label, model_name = historical_model._meta.label_lower.split(".")
                content_type = ContentType.objects.get(
                    app_label=app_label, model=model_name
                )
                if not dry_run and clear_existing:
                    Permission.objects.filter(content_type=content_type).delete()
                for action in actions:
                    name = f"Can {action} {historical_model._meta.verbose_name}"
                    codename = f"{action}_{model_name}"
                    try:
                        perm = Permission.objects.get(
                            content_type=content_type, codename=codename
                        )
                    except ObjectDoesNotExist:
                        if not dry_run:
                            Permission.objects.create(
                                content_type=content_type, name=name, codename=codename
                            )
                        created_codenames.append(codename)
                    else:
                        if perm.name != name:
                            if not dry_run:
                                perm.name = name
                                perm.save()
                            updated_names.append(name)
    if dry_run:
        print("This is a dry-run. No modifications were made.")
    if created_codenames:
        print("The following permission.codenames were be added:")
        pprint(created_codenames)
    else:
        print("No permission.codenames were added.")
    if updated_names:
        print("The following permission.names were updated:")
        pprint(updated_names)
    else:
        print("No permission.names were updated.")


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
