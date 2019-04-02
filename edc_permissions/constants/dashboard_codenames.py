from .group_names import AUDITOR, LAB, REVIEW, CLINIC, LAB_VIEW

LAB_DASHBOARD_CODENAMES = [
    ("view_lab_requisition_listboard", "Can view Lab requisition listboard"),
    ("view_lab_receive_listboard", "Can view Lab receive listboard"),
    ("view_lab_process_listboard", "Can view Lab process listboard"),
    ("view_lab_pack_listboard", "Can view Lab pack listboard"),
    ("view_lab_aliquot_listboard", "Can view Lab aliquot listboard"),
    ("view_lab_box_listboard", "Can view Lab box listboard"),
    ("view_lab_result_listboard", "Can view Lab result listboard"),
    ("view_lab_manifest_listboard", "Can view Lab manifest listboard"),
]

LAB_VIEW_DASHBOARD_CODENAMES = [
    ("view_lab_requisition_listboard", "Can view Lab requisition listboard"),
    ("view_lab_receive_listboard", "Can view Lab receive listboard"),
    ("view_lab_process_listboard", "Can view Lab process listboard"),
    ("view_lab_pack_listboard", "Can view Lab pack listboard"),
    ("view_lab_aliquot_listboard", "Can view Lab aliquot listboard"),
    ("view_lab_box_listboard", "Can view Lab box listboard"),
    ("view_lab_result_listboard", "Can view Lab result listboard"),
    ("view_lab_manifest_listboard", "Can view Lab manifest listboard"),
]

REVIEW_DASHBOARD_CODENAMES = [
    ("view_subject_review_listboard", "Can view Subject review listboard")
]

CLINIC_DASHBOARD_CODENAMES = LAB_VIEW_DASHBOARD_CODENAMES + REVIEW_DASHBOARD_CODENAMES
AUDITOR_DASHBOARD_CODENAMES = LAB_VIEW_DASHBOARD_CODENAMES + REVIEW_DASHBOARD_CODENAMES


DASHBOARD_CODENAMES = {
    LAB: LAB_DASHBOARD_CODENAMES,
    LAB_VIEW: LAB_VIEW_DASHBOARD_CODENAMES,
    REVIEW: REVIEW_DASHBOARD_CODENAMES,
    CLINIC: CLINIC_DASHBOARD_CODENAMES,
    AUDITOR: AUDITOR_DASHBOARD_CODENAMES,
}
