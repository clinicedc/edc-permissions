from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(
        url='/edc_permissions/admin/'), name='home_url'),
]

if settings.APP_NAME == 'edc_permissions':
    from edc_dashboard.views import AdministrationView
    urlpatterns += [
        path('accounts/', include('edc_auth.urls')),
        path('edc_base/', include('edc_base.urls')),
        path('edc_export/', include('edc_export.urls')),
        path('edc_lab/', include('edc_lab.urls')),
        path('edc_lab_dashboard/', include('edc_lab_dashboard.urls')),
        path('edc_pharmacy/', include('edc_pharmacy.urls')),
        # path('edc_pharmacy_dashboard/', include('edc_pharmacy_dashboard.urls')),
        path('administration/', AdministrationView.as_view(),
             name='administration_url'),
    ]
