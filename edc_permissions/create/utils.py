from django.apps import apps as django_apps
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from edc_permissions.utils import get_from_codename_tuple


def create_permissions_from_tuples(model, codename_tpls):
    """Creates custom permissions on "model".
    """
    if codename_tpls:
        model_cls = django_apps.get_model(model)
        content_type = ContentType.objects.get_for_model(model_cls)
        for codename_tpl in codename_tpls:
            _, codename, name = get_from_codename_tuple(
                codename_tpl, model_cls._meta.app_label
            )
            try:
                Permission.objects.get(
                    codename=codename, content_type=content_type)
            except ObjectDoesNotExist:
                Permission.objects.create(
                    name=name, codename=codename, content_type=content_type
                )
