# -*- coding: utf-8 -*-

from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import include, path, re_path
from resturant.endpoints import Index, handler_page_not_found_404
from django.shortcuts import render


handler404 = handler_page_not_found_404

urlpatterns = [
    re_path(r"^$", Index.as_view(), name="index"),
    path("admin/", admin.site.urls),
    path("restaurant/", include("resturant.urls")),
    path("", include("django_prometheus.urls")),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
] + debug_toolbar_urls()



