from .codenames import DEFAULT_CODENAMES
from .group_names import (
    ACCOUNT_MANAGER, ADMINISTRATION,
    EVERYONE, AUDITOR, CLINIC, LAB, PHARMACY, PII)


DEFAULT_AUDITOR_APP_LABELS = ['edc_lab', 'edc_offstudy']

DEFAULT_GROUP_NAMES = [
    ACCOUNT_MANAGER,
    ADMINISTRATION,
    AUDITOR,
    CLINIC,
    EVERYONE,
    LAB,
    PHARMACY,
    PII]

DEFAULT_PII_MODELS = [
    'edc_locator.subjectlocator',
    'edc_registration.registeredsubject']
