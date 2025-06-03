# -*- coding: utf-8 -*-


from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

from applications.resturant.endpoints import (
    Index,
    handle_unauthorized_error_403,
    handler_page_not_found_404,
    handler_server_error_500,
)

handler404 = handler_page_not_found_404
handler500 = handler_server_error_500
handler403 = handle_unauthorized_error_403
urlpatterns = [
    re_path(r"^$", Index.as_view(), name="index"),
    path("admin/", admin.site.urls),
    path("restaurant/", include("applications.resturant.urls")),
    path("", include("django_prometheus.urls")),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
    re_path(r"^checkup/", include("health_check.urls")),
    path("byte_patrol/", include("applications.byte_patrol.urls")),
    *debug_toolbar_urls(),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
