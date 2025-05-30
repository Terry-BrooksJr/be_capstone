import sys
import os
from django.shortcuts import render
from django.views.generic import TemplateView
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from loguru import logger
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from applications.resturant.filters import BookingFilter, ProductFilter
from applications.resturant.models import Booking, Menu
from applications.resturant.serializers.core import (
    BookingSerializer,
    MenuSerializer,
)
from utils.cache import CachedResponseMixin

# Remove all existing handlers to avoid duplicate logs
logger.remove()

# Add a single stream handler (stdout)
logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")

# Ensure the log directory exists
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# Add a file handler
logger.add(
    os.path.join(log_dir, "info.log"),
    format="{time} {level} {message}",
    level="DEBUG",
    enqueue=True  # Good practice for multi-threaded/multi-process apps
)


def handler_page_not_found_404(request, exception):
    logger.warning(f"Page Not Found: {request.path} - Error{exception}")
    return render(request, "404.html", status=404)


def handler_server_error_500(request):
    logger.error(f"Server Error: {request.path}")
    return render(request, "500.html", status=500)


class Index(CachedResponseMixin, TemplateView):
    """A view for rendering the index template.

    This view simply renders the 'index.html' template.
    """

    primary_model = None
    template_name = "index.html"


# ----- BOOKING VIEWS -----


@extend_schema(
    summary="List All Current Bookings",
    description="Retrieve a list of all Little Lemon Bookings in the system. Authentication Token REQUIRED",
    parameters=None,
    tags=["Reservations"],
    # auth=["authToken"],
    filters=True,
    responses=BookingSerializer,
    examples=[
        OpenApiExample(
            name="Successful GET request",
            description="Shows the expected payload and shape of resoruces when a successful GET request is made.",
            value=[
                {
                    "booking_id": 123,
                    "name": "Albus Dumbledore",
                    "no_of_guests": 2,
                    "date": "01-01-1970",
                    "time": "3:45 PM",
                },
                {
                    "booking_id": 125,
                    "name": "Hermoine Granger",
                    "no_of_guests": 8,
                    "date": "01-02-1970",
                    "time": "5:45 PM",
                },
            ],
            status_codes=[status.HTTP_200_OK],
        )
    ],
)
class BookingListView(CachedResponseMixin, generics.ListAPIView):
    """Provides endpoint for listing all bookings."""

    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    filter_backends = [DjangoFilterBackend]
    search_fields = ["name"]
    filterset_class = BookingFilter
    ordering_fields = ["date", "no_of_guests"]
    permission_classes = [IsAuthenticated]


class BookingCreateView(CachedResponseMixin, generics.CreateAPIView):
    """Provides endpoint for creating bookings."""

    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Create a Booking",
        description="Create a new booking entry. All fields are required in the request payload. Authentication Token REQUIRED.",
        request=BookingSerializer,
        tags=["Reservations"],
        # auth=["TokenAuth"],
        examples=[
            OpenApiExample(
                "Create Booking POST body Example",
                description="Example POST Body  for creating a booking",
                value={
                    "name": "Sirus Black",
                    "no_of_guests": 4,
                    "date": "2025-04-03",
                    "time": "11:00AM",
                },
                request_only=True,
                response_only=False,
                status_codes=[status.HTTP_201_CREATED],
            ),
            OpenApiExample(
                "Create Booking Response Payload Example",
                description="Example payload for creating a booking",
                value={
                    "status": "booked",
                    "message": "We look forward to seeing your party of 7 on 05-11-2045 at 10:55 PM",
                    "details": {
                        "booking_id": 69,
                        "name": "Pacocha, Rhoda",
                        "no_of_guests": 7,
                        "date": "05-11-2045",
                        "time": "10:55 PM",
                    },
                },
                request_only=False,
                response_only=True,
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            return {
                "status": (
                    "booked"
                    if "booking_id" in serializer.validated_data.keys()
                    else "not booked"
                ),
                "message": (
                    f"We look forward to seeing your party of {serializer.validated_data["no_of_guests"]} on {representation["date"]} at {serializer.validated_data['time']}"
                    if "booking_id" in serializer.validated_data.keys()
                    else "Booking not created"
                ),
                "details": representation,
            }
        return Response(
            data={"message": "Authentication credentials were not provided."},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class BookingView(CachedResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    """Provides endpoints for retrieving, updating, and deleting a specific booking."""

    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    lookup_field = "booking_id"
    primary_model = Booking
    filter_backends = [DjangoFilterBackend]
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    @extend_schema(
        summary="Retrieve Specific Booking By ID",
        auth=None,
        tags=["Reservations"],
        description="Get the details of a specific booking by its ID.",
        responses=BookingSerializer,
        filters=False,
        parameters=[
            OpenApiParameter(
                name="booking_id",
                type=OpenApiTypes.INT,
                location="path",
                required=True,
                description="Unique Numeric Identifer",
                examples=[OpenApiExample(name="Standard Booking ID", value="123")],
            )
        ],
        examples=[
            OpenApiExample(
                name="Successful GET request",
                description="Shows the expected payload and shape of resoruces when a successful GET request is made.",
                value=[
                    {
                        "booking_id": 123,
                        "name": "Tom Riddle",
                        "no_of_guests": 2,
                        "date": "01-01-1970",
                        "time": "3:45 PM",
                    },
                ],
                status_codes=[status.HTTP_200_OK],
            ),
            OpenApiExample(
                name="Booking ID Not Found",
                description="Example respose payload for updating a booking when booking ID is not found",
                value={
                    "details": {
                        "error": "Booking ID not found",
                    }
                },
                request_only=False,
                response_only=True,
                status_codes=[status.HTTP_404_NOT_FOUND],
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update a Booking",
        description="Update an existing booking. Authentication Token REQUIRED.",
        # auth=["TokenAuth"],
        tags=["Reservations"],
        responses=BookingSerializer,
        parameters=[
            OpenApiParameter(
                name="booking_id",
                type=OpenApiTypes.INT,
                location="path",
                required=True,
                description="Unique Numeric Identifer",
                examples=[OpenApiExample(name="Standard Booking ID", value="123")],
            )
        ],
        examples=[
            OpenApiExample(
                "Success  - Update Booking Example",
                description="Example request body for updating a booking",
                value={
                    "name": "Dolores Umbridge",
                    "no_of_guests": 4,
                    "date": "2025-04-03",
                    "time": "11:00AM",
                },
                request_only=True,
                response_only=False,
                status_codes=[status.HTTP_200_OK],
            ),
            OpenApiExample(
                "Fail - Not Providing All Field Example",
                description="Unsuccessful Request Body for updating a booking",
                value={
                    "name": "Bellatrix Lestrange",
                    "no_of_guests": 4,
                },
                request_only=True,
                response_only=False,
                status_codes=[status.HTTP_400_BAD_REQUEST],
            ),
            OpenApiExample(
                "Update Booking Example",
                description="Example respose payload for updating a booking",
                value={
                    "name": "Rubeus Hagrid",
                    "no_of_guests": 4,
                    "date": "2025-04-03T11:00:00Z",
                },
                request_only=False,
                response_only=True,
                status_codes=[status.HTTP_200_OK],
            ),
            OpenApiExample(
                "Update Booking Example - Booking ID Not Found",
                description="Example respose payload for updating a booking when booking ID is not found",
                value={
                    "details": {
                        "error": "Booking ID not found",
                    }
                },
                request_only=False,
                response_only=True,
                status_codes=[status.HTTP_404_NOT_FOUND],
            ),
        ],
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Delete a Booking",
        description="Delete a booking entry. Authentication Token REQUIRED.",
        tags=["Reservations"],
        # auth=["TokenAuth"],
        responses=BookingSerializer,
        parameters=[
            OpenApiParameter(
                name="booking_id",
                type=OpenApiTypes.INT,
                location="path",
                required=True,
                description="Unique Numeric Identifer",
                examples=[OpenApiExample(name="Standard Booking ID", value="123")],
            )
        ],
        examples=[
            OpenApiExample(
                "Delete Booking Example",
                description="Example request body for deleting a booking",
                value={
                    "booking_id": 123,
                },
                request_only=True,
                response_only=False,
                status_codes=[status.HTTP_204_NO_CONTENT],
            ),
        ],
    )
    def delete(self, request, *args, **kwargs):
        """Delete a booking entry."""
        return super().delete(request, *args, **kwargs)

    @extend_schema(
        summary="Partially Update a Booking",
        description="Update partial fields of a booking. Authentication Token REQUIRED.",
        # auth=["TokenAuth"],
        tags=["Reservations"],
        responses=BookingSerializer,
        parameters=[
            OpenApiParameter(
                name="booking_id",
                type=OpenApiTypes.INT,
                location="path",
                required=True,
                description="Unique Numeric Identifer",
                examples=[OpenApiExample(name="Standard Booking ID", value="123")],
            )
        ],
        examples=[
            OpenApiExample(
                "Successful Partial Update Booking PATCH Request Body Example",
                description="Example request body for updating a booking",
                value={
                    "booking_id": 542,
                    "name": "Minerva McGonagall",
                    "no_of_guests": 4,
                },
                request_only=True,
                response_only=False,
                status_codes=[status.HTTP_200_OK],
            ),
            OpenApiExample(
                "Partial Update Booking PATCH Response Body Example -  Booking ID Not Found",
                description="Example respose payload for updating a booking when booking ID is not found",
                value={
                    "details": {
                        "error": "Booking ID not found",
                    }
                },
                request_only=False,
                response_only=True,
                status_codes=[status.HTTP_400_BAD_REQUEST],
            ),
        ],
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


# ----- MENU VIEWS -----


@extend_schema(
    summary="List All Menu Items",
    description="Retrieve a list of all Little Lemon Menu Items in the system.",
    auth=None,
    parameters=None,
    tags=["Menu"],
    filters=True,
    responses=MenuSerializer,
    examples=[
        OpenApiExample(
            name="Successful GET request",
            description="Shows the expected payload and shape of resources when a successful GET request is made.",
            value=[
                {
                    "item_id": 1,
                    "title": "Greek Salad",
                    "price": 12.99,
                    "inventory": 100,
                    "category": "Appetizer",
                },
                {
                    "item_id": 2,
                    "title": "Grilled Fish",
                    "price": 21.99,
                    "inventory": 50,
                    "category": "Main",
                },
            ],
            status_codes=[status.HTTP_200_OK],
        )
    ],
)
class MenuListView(CachedResponseMixin, generics.ListAPIView):
    """Provides endpoint for listing all menu items."""

    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    filter_backends = [DjangoFilterBackend]
    search_fields = ["title"]
    filterset_class = ProductFilter
    permission_classes = [IsAuthenticated]


@extend_schema(
    summary="Create a Menu Item",
    description="Create a new menu item entry. All fields are required in the request payload.",
    request=MenuSerializer,
    tags=["Menu"],
    auth=None,
    responses=MenuSerializer,
    examples=[
        OpenApiExample(
            "Create Menu Item Example",
            description="Example payload for creating a menu item",
            value={
                "title": "Baklava",
                "price": 8.99,
                "inventory": 25,
                "category": "Dessert",
            },
            response_only=False,
            status_codes=[status.HTTP_201_CREATED],
        )
    ],
)
class MenuCreateView(CachedResponseMixin, generics.CreateAPIView):
    """Provides endpoint for creating menu items."""

    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [IsAuthenticated]


# Combined view that supports multiple operations on a single endpoint
class MenuView(CachedResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    """Provides endpoints for retrieving, updating, and deleting a specific menu item."""

    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    primary_model = Menu
    lookup_field = "item_id"
    filter_backends = [DjangoFilterBackend]
    search_fields = ["title"]
    filterset_class = ProductFilter
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Retrieve Specific Menu Item By ID",
        auth=None,
        tags=["Menu"],
        description="Get the details of a specific menu item by its ID.",
        responses=MenuSerializer,
        filters=False,
        parameters=[
            OpenApiParameter(
                name="item_id",
                type=OpenApiTypes.INT,
                location="path",
                required=True,
                description="Unique Numeric Identifier",
                examples=[OpenApiExample(name="Standard Item ID", value="1")],
            )
        ],
        examples=[
            OpenApiExample(
                name="Successful GET request",
                description="Shows the expected payload and shape of resources when a successful GET request is made.",
                value={
                    "item_id": 1,
                    "title": "Greek Salad",
                    "price": 12.99,
                    "inventory": 100,
                    "category": "Appetizer",
                },
                status_codes=[status.HTTP_200_OK],
            ),
            OpenApiExample(
                name="Item ID Not Found",
                description="When a resource is not found based on the provided Item ID",
                value="""
                { "Error": "No Menu Item with Provided ID Found"}
                """,
                status_codes=[status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST],
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Delete a Menu Item",
        description="Remove a menu item from the system.",
        parameters=[
            OpenApiParameter(
                name="item_id",
                type=OpenApiTypes.INT,
                location="path",
                required=True,
                description="Unique Numeric Identifier",
                examples=[OpenApiExample(name="Standard Item ID", value="1")],
            )
        ],
        examples=[
            OpenApiExample(
                name="Successful DELETE request",
                description="Shows the expected payload and shape of resources when a successful DELETE request is made.",
                value={"message": "Menu item with ID 1 has been deleted successfully."},
                status_codes=[status.HTTP_204_NO_CONTENT],
                response_only=True,
            ),
            OpenApiExample(
                name="Item ID Not Found",
                description="When a resource is not found based on the provided Item ID",
                value="""
                    { "Error": "No Menu Item with Provided ID Found"}
                    """,
                status_codes=[status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST],
            ),
        ],
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    @extend_schema(
        summary="Partial Update of a Menu Item",
        tags=["Menu"],
        description="Update one or more fields of an existing menu item.",
        parameters=[
            OpenApiParameter(
                name="item_id",
                type=OpenApiTypes.INT,
                location="path",
                required=True,
                description="Unique Numeric Identifier",
                examples=[OpenApiExample(name="Standard Item ID", value="1")],
            )
        ],
        examples=[
            OpenApiExample(
                name="Successful PATCH request",
                description="Shows the expected payload and shape of resources when a successful PATCH request is made.",
                value={
                    "price": 5.99,
                    "inventory": 100,
                },
                status_codes=[status.HTTP_200_OK],
                request_only=True,
                response_only=False,
            ),
            OpenApiExample(
                name="Item ID Not Found",
                description="When a resource is not found based on the provided Item ID",
                value="""
                    { "Error": "No Menu Item with Provided ID Found"}
                    """,
                status_codes=[status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST],
                request_only=False,
                response_only=True,
            ),
            OpenApiExample(
                name="Invalid Method - Adding All Fields to a PATCH request",
                description="When all fields are provided in a PATCH request. Pleawew use a PUT request.",
                value={
                    "item_id": 1,
                    "title": "Green Apple Salad",
                    "price": 5.99,
                    "inventory": 100,
                },
                status_codes=[
                    status.HTTP_405_METHOD_NOT_ALLOWED,
                    status.HTTP_400_BAD_REQUEST,
                ],
                response_only=True,
                request_only=False,
            ),
        ],
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary="Update a Menu Item",
        tags=["Menu"],
        description="Update all details of an existing menu item.",
        parameters=[
            OpenApiParameter(
                name="item_id",
                type=OpenApiTypes.INT,
                location="path",
                required=True,
                description="Unique Numeric Identifier",
                examples=[OpenApiExample(name="Standard Item ID", value="1")],
            )
        ],
        examples=[
            OpenApiExample(
                name="Successful PUT request",
                description="Shows the expected payload and shape of resources when a successful PUT request is made.",
                value={
                    "title": "Greek Salad",
                    "price": 12.99,
                    "inventory": 100,
                },
                status_codes=[status.HTTP_200_OK],
                request_only=True,
                response_only=False,
            ),
            OpenApiExample(
                name="Item ID Not Found",
                description="When a resource is not found based on the provided Item ID",
                value="""
                        { "Error": "No Menu Item with Provided ID Found"}
                        """,
                status_codes=[status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST],
                request_only=False,
                response_only=True,
            ),
            OpenApiExample(
                name="Invalid Method - Missing Fields to a PUT request",
                description="When Not All fields are provided in a PUT request. Please use a PATCH request.",
                value={
                    "price": 12.99,
                    "inventory": 100,
                },
                status_codes=[
                    status.HTTP_405_METHOD_NOT_ALLOWED,
                    status.HTTP_400_BAD_REQUEST,
                ],
                response_only=True,
                request_only=False,
            ),
        ],
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
