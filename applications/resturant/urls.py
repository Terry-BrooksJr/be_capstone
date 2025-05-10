from django.urls import path, re_path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter

from applications.resturant import cbv_endpoints, endpoints

router = DefaultRouter()
router.register(r"bookings", endpoints.BookingsViewset, basename="bookings")
router.register(r"menu", endpoints.MenuViewset, basename="menu")
urlpatterns = [
    # path("", include(router.urls)),
    path("swagger/", SpectacularSwaggerView.as_view(), name="swagger"),
    path("redoc/", SpectacularRedocView.as_view(), name="redoc"),
    path("schema", SpectacularAPIView.as_view(), name="schema"),
    re_path(r"^bookings/?$", cbv_endpoints.BookingListView.as_view(), name="bookings-list"),
    re_path(r"^bookings/create/?$", cbv_endpoints.BookingCreateView.as_view(), name="bookings-create"),
    re_path(r"^bookings/(?P<booking_id>\d{1,5})/?$", cbv_endpoints.BookingView.as_view(), name="bookings-detail"),
    re_path(r"^menu/?$", cbv_endpoints.MenuListView.as_view(), name="menu-list"),
    re_path(r"^menu/(?P<pk>\d{1,5})/?$", cbv_endpoints.MenuView.as_view(), name="menu-detail"),
    re_path(r"^menu/create/?$", cbv_endpoints.MenuCreateView.as_view(), name="menu-create"),
]
