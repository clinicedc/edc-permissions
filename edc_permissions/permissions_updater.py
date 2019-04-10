from .groups_updater import GroupsUpdater
from .utils import (
    create_edc_dashboard_permissions,
    create_edc_navbar_permissions,
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
    update_pii_view_group_permissions,
)


class PermissionsUpdater:
    def __init__(
        self, extra_pii_models=None, extra_updaters=None, extra_group_names=None
    ):

        GroupsUpdater(extra_group_names=extra_group_names)

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
        update_pii_group_permissions(extra_pii_models=extra_pii_models)
        update_pii_view_group_permissions(extra_pii_models=extra_pii_models)

        for updater in extra_updaters or []:
            updater()
