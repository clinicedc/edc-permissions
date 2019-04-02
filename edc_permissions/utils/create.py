from django.contrib.auth.models import Group

from ..constants import NAVBAR_CODENAMES, DASHBOARD_CODENAMES
from .generic import (
    create_permissions_from_tuples,
    remove_permissions_from_group_by_codenames,
)


def create_edc_dashboard_permissions(extra_codenames=None):
    model = "edc_dashboard.dashboard"
    for _, codename_tpls in DASHBOARD_CODENAMES.items():
        create_permissions_from_tuples(model, codename_tpls)
    create_permissions_from_tuples(model, extra_codenames)
    for group in Group.objects.all():
        remove_permissions_from_group_by_codenames(
            group=group,
            codenames=[
                "add_dashboard",
                "change_dashboard",
                "delete_dashboard",
                "view_dashboard",
            ],
        )


def create_edc_navbar_permissions(extra_codenames=None):
    model = "edc_navbar.navbar"
    for _, codename_tpls in NAVBAR_CODENAMES.items():
        create_permissions_from_tuples(model, codename_tpls)
    for codename_tpls in extra_codenames or []:
        create_permissions_from_tuples(model, codename_tpls)
    for group in Group.objects.all():
        remove_permissions_from_group_by_codenames(
            group=group,
            codenames=["add_navbar", "change_navbar",
                       "delete_navbar", "view_navbar"],
        )
