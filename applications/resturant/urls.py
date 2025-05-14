from django.urls import path, re_path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from resturant import endpoints

urlpatterns = [
    # path("", include(router.urls)),
    path("swagger/", SpectacularSwaggerView.as_view(), name="swagger"),
    path("redoc/", SpectacularRedocView.as_view(), name="redoc"),
    path("schema", SpectacularAPIView.as_view(), name="schema"),
    re_path(r"^bookings/?$", endpoints.BookingListView.as_view(), name="bookings-list"),
    re_path(
        r"^bookings/create/?$",
        endpoints.BookingCreateView.as_view(),
        name="bookings-create",
    ),
    re_path(
        r"^bookings/(?P<booking_id>\d{1,5})/?$",
        endpoints.BookingView.as_view(),
        name="bookings-detail",
    ),
    re_path(r"^menu/?$", endpoints.MenuListView.as_view(), name="menu-list"),
    re_path(
        r"^menu/(?P<item_id>\d{1,5})/?$",
        endpoints.MenuView.as_view(),
        name="menu-detail",
    ),
    re_path(r"^menu/create/?$", endpoints.MenuCreateView.as_view(), name="menu-create"),
]
