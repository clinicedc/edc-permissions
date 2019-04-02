from django.contrib.auth.models import Group

from ..utils import remove_permissions_from_group_by_codenames
from ..constants import NAVBAR_CODENAMES
from .utils import create_permissions_from_tuples


def create_edc_navbar_permissions(extra_codenames=None):
    model = "edc_navbar.navbar"
    for _, codename_tpls in NAVBAR_CODENAMES.items():
        create_permissions_from_tuples(model, codename_tpls)
    for codename_tpls in extra_codenames or []:
        create_permissions_from_tuples(model, codename_tpls)
    for group in Group.objects.all():
        remove_permissions_from_group_by_codenames(
            group=group,
            codenames=["add_navbar", "change_navbar", "delete_navbar", "view_navbar"],
        )
