from .group_names import (
    ADMINISTRATION,
    AUDITOR,
    CLINIC,
    LAB,
    LAB_VIEW,
    PHARMACY,
    EVERYONE,
)

NAVBAR_CODENAMES = {
    ADMINISTRATION: ["edc_navbar.nav_administration"],
    AUDITOR: ["edc_navbar.nav_lab_section", "edc_navbar.nav_lab_requisition"],
    CLINIC: ["edc_navbar.nav_lab_section", "edc_navbar.nav_lab_requisition"],
    EVERYONE: [
        "edc_navbar.nav_administration",
        "edc_navbar.nav_home",
        "edc_navbar.nav_logout",
        "edc_navbar.nav_public",
    ],
    LAB: [
        "edc_navbar.nav_lab_section",
        "edc_navbar.nav_lab_requisition",
        "edc_navbar.nav_lab_receive",
        "edc_navbar.nav_lab_process",
        "edc_navbar.nav_lab_pack",
        "edc_navbar.nav_lab_manifest",
        "edc_navbar.nav_lab_aliquot",
    ],
    LAB_VIEW: [
        "edc_navbar.nav_lab_section",
        "edc_navbar.nav_lab_requisition",
        "edc_navbar.nav_lab_receive",
        "edc_navbar.nav_lab_process",
        "edc_navbar.nav_lab_pack",
        "edc_navbar.nav_lab_manifest",
        "edc_navbar.nav_lab_aliquot",
    ],
    PHARMACY: ["edc_navbar.nav_pharmacy_section"],
}


for group_name, codenames in NAVBAR_CODENAMES.items():
    updated_codenames = []
    for codename in codenames:
        updated_codenames.append((codename, f"Can access {codename.split('.')[1]}"))
    NAVBAR_CODENAMES[group_name] = updated_codenames
