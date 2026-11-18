"""
URL Configuration for HoneyChain Project
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views as config_views

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # Public pages
    path('', config_views.home_view, name='home'),
    path('about/', config_views.about_view, name='about'),

    # Authentication: login, logout, register, dashboard
    path('accounts/', include('accounts.urls', namespace='accounts')),

    # Apiary management (login required)
    path('apiaries/', include('apiaries.urls', namespace='apiaries')),

    # Bee colony management (login required)
    path('colonies/', include('colonies.urls', namespace='colonies')),

    # Honey batch management (login required)
    path('honey/', include('honey.urls', namespace='honey')),

    # Public customer traceability / QR verification
    path('verify/', include('traceability.urls', namespace='traceability')),
]

# Serve media and static files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler403 = 'django.views.defaults.permission_denied'
handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'
