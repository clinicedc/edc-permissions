from .create import create_edc_dashboard_permissions, create_edc_navbar_permissions
from .groups_updater import GroupsUpdater
from .update import (
    update_account_manager_group_permissions,
    update_administration_group_permissions,
    update_auditor_group_permissions,
    update_clinic_group_permissions,
    update_data_manager_group_permissions,
    update_everyone_group_permissions,
    update_export_group_permissions,
    update_lab_group_permissions,
    update_lab_view_group_permissions,
    update_pharmacy_group_permissions,
    update_pii_group_permissions,
)


class PermissionsUpdater:
    def __init__(self, verbose=None):

        GroupsUpdater()

        create_edc_dashboard_permissions()
        create_edc_navbar_permissions()

        update_account_manager_group_permissions()
        update_administration_group_permissions()
        update_auditor_group_permissions()
        update_clinic_group_permissions()
        update_data_manager_group_permissions()
        update_everyone_group_permissions()
        update_export_group_permissions()
        update_lab_group_permissions()
        update_lab_view_group_permissions()
        update_pharmacy_group_permissions()
        update_pii_group_permissions()
