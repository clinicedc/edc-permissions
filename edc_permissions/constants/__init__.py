from .default_codenames import DEFAULT_CODENAMES
from .group_names import (
    ACCOUNT_MANAGER, ADMINISTRATION, PII_VIEW,
    EVERYONE, AUDITOR, CLINIC, LAB, PHARMACY, PII,
    EXPORT)
from .lab_dashboard_codenames import LAB_DASHBOARD_CODENAMES

DEFAULT_AUDITOR_APP_LABELS = ['edc_lab', 'edc_offstudy']

DEFAULT_GROUP_NAMES = [
    ACCOUNT_MANAGER,
    ADMINISTRATION,
    AUDITOR,
    CLINIC,
    EVERYONE,
    EXPORT,
    LAB,
    PHARMACY,
    PII,
    PII_VIEW]

DEFAULT_PII_MODELS = [
    'edc_locator.subjectlocator',
    'edc_registration.registeredsubject']
