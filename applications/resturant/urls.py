from django.urls import include, path
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)
from rest_framework.routers import DefaultRouter

from applications.resturant import endpoints, cbv_endpoints

router = DefaultRouter()
router.register(r"bookings", endpoints.BookingsViewset, basename="bookings")
router.register(r"menu", endpoints.MenuViewset, basename="menu")
urlpatterns = [
    # path("", include(router.urls)),
    path("swagger/", SpectacularSwaggerView.as_view(), name="swagger"),
    path("redoc/", SpectacularRedocView.as_view(), name="redoc"),
    path("schema", SpectacularAPIView.as_view(), name="schema"),
    path('bookings/', cbv_endpoints.BookingListView.as_view(), name='bookings-list'),
    path('bookings/create', cbv_endpoints.BookingCreateView.as_view(), name='bookings-create'),  
    path('bookings/<int:booking_id>/', cbv_endpoints.BookingView.as_view(), name='bookings-detail'), 
]
