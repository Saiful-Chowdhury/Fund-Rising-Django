# donation_platform/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from organization_dashboard.views import home_view
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # Include core app URLs
     path('auth/', include('organization_auth.urls')), # For organization registration/login
    path('organization-panel/', include('organization_dashboard.urls')), # Organization's custom dashboard
    path('', home_view, name='home'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)