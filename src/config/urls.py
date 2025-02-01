from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path(route='admin/', view=admin.site.urls),
    path(route='', view=include(('ticketing_system.authentication.urls', 'auth'))),
    path(route='tickets/', view=include(('ticketing_system.ticket.urls', 'tickets'))),
]


if settings.DEBUG:
    urlpatterns.append(path(route="__debug__/", view=include("debug_toolbar.urls")))
    urlpatterns.append(path(route='api-auth/', view=include('rest_framework.urls')))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
