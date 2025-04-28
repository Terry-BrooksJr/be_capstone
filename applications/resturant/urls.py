from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter

from applications.resturant import endpoints

router = DefaultRouter()
router.register(r"bookings", endpoints.BookingsViewset)
router.register(r"menu", endpoints.MenuViewset)
urlpatterns = [
    path("", include(router.urls)),
    path("swagger/", SpectacularSwaggerView.as_view(), name="swagger"),
    path("redoc/", SpectacularRedocView.as_view(), name="redoc"),
    path("schema", SpectacularAPIView.as_view(), name="schema"),
]
