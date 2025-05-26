# -*- coding: utf-8 -*-

from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from resturant.endpoints import Index, handler_page_not_found_404

handler404 = handler_page_not_found_404

urlpatterns = [
    re_path(r"^$", Index.as_view(), name="index"),
    path("admin/", admin.site.urls),
    path("restaurant/", include("resturant.urls")),
    path("", include("django_prometheus.urls")),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
    re_path(r"^checkup/", include("health_check.urls")),
] + debug_toolbar_urls()


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
