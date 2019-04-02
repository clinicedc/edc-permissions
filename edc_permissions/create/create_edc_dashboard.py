from django.contrib.auth.models import Group

from ..constants import DASHBOARD_CODENAMES
from ..utils import remove_permissions_from_group_by_codenames
from .utils import create_permissions_from_tuples


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
