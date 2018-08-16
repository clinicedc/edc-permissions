from django.conf import settings
import sys

if settings.APP_NAME == 'edc_permissions' and 'test' in sys.argv:
    from .tests.models import *   # noqa
