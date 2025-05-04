# Create your views here.
from django.views.generic import TemplateView
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet
from resturant.serializers.core import BookingSerializer, MenuSerializer, UserSerializer
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from applications.resturant.filters import BookingFilter, ProductFilter
from applications.resturant.models import Booking, Menu
from applications.resturant.serializers.auth import AuthRequestSerializer

class Index(TemplateView):
    """A view for rendering the index template.

    This view simply renders the 'index.html' template.
    """

    template_name = "index.html"


class AuthToken(ObtainAuthToken):
    """A custom view for handling user authentication and token generation."""
    @extend_schema(
        summary="User Authentication",
        description="Authenticate a user and generate an authentication token.",
        tags=["Tokens"],
        request=AuthRequestSerializer,
        responses=UserSerializer,
        examples=[
            OpenApiExample(
                name="Successful Authentication",
                description="Valid credentials",
                value={"username": "john_doe", "password": "password123"},
                request_only=True,
            ),
            OpenApiExample(
                name="Invalid Login Attempt",
                description="Incorrect username or password",
                value={"username": "wrong_user", "password": "wrong_pass"},
                request_only=True,
            ),
            OpenApiExample(
                name="Successful Response",
                description="Token returned after successful login",
                value={
                    "token": "abcdef123456",
                    "user_id": 1,
                    "email": "john.doe@example.com"
                },
                response_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get("user")
        if user is None:
            from rest_framework.exceptions import AuthenticationFailed
            raise AuthenticationFailed("User not found in validated data")
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user_id": user.pk, "email": user.email})


@extend_schema_view(
    list=extend_schema(
        summary="List All Current Bookings",
        description="Retrieve a list of all Little Lemon Bookings in the system.",
        auth=None,
        parameters=None,
        tags=["Reservations"],
        filters=True,
        responses=BookingSerializer,
        examples=[
            OpenApiExample(
                name="Successful GET request",
                description="Shows the expected payload and shape of resoruces when  a successfukl GET request is made.",
                value=[
                    {
                        "booking_id": 123,
                        "name": "John Doe",
                        "no_of_guests": 2,
                        "date": "01-01-1970",
                        "time": "3:45 PM",
                    },
                    {
                        "booking_id": 125,
                        "name": "Jane Doe",
                        "no_of_guests": 8,
                        "date": "01-02-1970",
                        "time": "5:45 PM",
                    },
                ],
                status_codes=[status.HTTP_200_OK],
            )
        ],
    ),
    retrieve=extend_schema(
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
                description="Unique Alphanumeric Identifer",
                examples=[OpenApiExample(name="Standard Booking ID", value="123")],
            )
        ],
        examples=[
            OpenApiExample(
                name="Successful GET request",
                description="Shows the expected payload and shape of resoruces when  a successful GET request is made.",
                value=[
                    {
                        "booking_id": 123,
                        "name": "John Doe",
                        "no_of_guests": 2,
                        "date": "01-01-1970",
                        "time": "3:45 PM",
                    },
                ],
                status_codes=[status.HTTP_200_OK],
            ),
            OpenApiExample(
                name="Booking ID Not Found",
                description="When a resource is not found based on the provided Booking ID",
                value="""
                            { "Error": " No Booking Provided ID Found"}
                            """,
                status_codes=[status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST],
            ),
        ],
    ),
    create=extend_schema(
        summary="Create a Booking",
        description="Create a new booking entry. All fields are required in the request payload. Authentication Token REQUIRED.",
        request=BookingSerializer,
        tags=["Reservations"],
        parameters=[
            OpenApiParameter(
                name="name",
                type=OpenApiTypes.STR,
                location="path",
                required=True,
                description="Name of the person making the booking",
                examples=[OpenApiExample(name="Standard Booking ID", value="John Doe")],
            ),
            OpenApiParameter(
                name="no_of_guests",
                type=OpenApiTypes.INT,
                location="path",
                required=True,
                description="Number of guests in the party",
                examples=[OpenApiExample(name="Standard Booking ID", value="123")],
            ),
            OpenApiParameter(
                name="date",
                type=OpenApiTypes.DATE,
                location="path",
                required=True,
                description="Date of the booking",
                examples=[
                    OpenApiExample(name="Standard Booking ID", value="01-01-1970")
                ],
            ),
            OpenApiParameter(
                name="time",
                type=OpenApiTypes.TIME,
                location="path",
                required=True,
                description="Time of the booking",
                examples=[OpenApiExample(name="Standard Booking ID", value="3:45 PM")],
            ),
        ],
        # auth=["TokenAuth"],
        responses=BookingSerializer,
        examples=[
            OpenApiExample(
                "Create Booking Example",
                description="Example POST Body  for creating a booking",
                value={
                    "name": "John Doe",
                    "no_of_guests": 4,
                    "date": "2025-04-03",
                    "time": "11:00AM",
                },
                request_only=True,
                response_only=False,
                status_codes=[status.HTTP_201_CREATED],
            ),
            OpenApiExample(
                "Create Booking Example",
                description="Example payload for creating a booking",
                value={
                    "name": "John Doe",
                    "no_of_guests": 4,
                    "date": "2025-04-03T11:00:00Z",
                },
                request_only=False,
                response_only=True,
                status_codes=[status.HTTP_201_CREATED],
            ),
        ],
    ),
    update=extend_schema(
        summary="Update a Booking",
        description="Update an existing booking. Authentication Token REQUIRED.",
        # auth=["TokenAuth"],
        tags=["Reservations"],
        responses=BookingSerializer,
        examples=[
            OpenApiExample(
                "Success  - Update Booking Example",
                description="Example request body for updating a booking",
                value={
                    "booking_id": 123,
                    "name": "John Doe",
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
                    "name": "John Doe",
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
                    "name": "John Doe",
                    "no_of_guests": 4,
                    "date": "2025-04-03T11:00:00Z",
                },
                request_only=False,
                response_only=True,
                status_codes=[status.HTTP_200_OK],
            ),
        ],
    ),
    partial_update=extend_schema(
        summary="Partially Update a Booking",
        description="Update partial fields of a booking. Authentication Token REQUIRED.",
        # auth=["TokenAuth"],
        tags=["Reservations"],
        responses=BookingSerializer,
        examples=[
            OpenApiExample(
                "Partial Update Booking Example",
                description="Example request body for updating a booking",
                value={
                    "name": "John Doe",
                    "no_of_guests": 4,
                },
                request_only=True,
                response_only=False,
                status_codes=[status.HTTP_200_OK],
            )
        ],
    ),
    destroy=extend_schema(
        summary="Delete a Booking",
        description="Delete a booking entry. Authentication Token REQUIRED.",
        tags=["Reservations"],
        # auth=["TokenAuth"],
        responses=BookingSerializer,
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
    ),
)
class BookingsViewset(ModelViewSet):
    """Provides endpoints for listing, retrieving, creating, updating, and deleting bookings."""

    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    lookup_field = "booking_id"
    filter_backends = [DjangoFilterBackend]
    search_fields = ["name"]
    filterset_class = BookingFilter
    ordering_fields = ["date", "no_of_guests"]
    permission_classes = [IsAuthenticated]


@extend_schema_view(
    list=extend_schema(
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
    ),
    retrieve=extend_schema(
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
                description="Unique Alphanumeric Identifier",
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
    ),
    create=extend_schema(
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
    ),
    update=extend_schema(
        summary="Update a Menu Item",
        tags=["Menu"],
        description="Update all details of an existing menu item.",
    ),
    partial_update=extend_schema(
        summary="Partial Update of a Menu Item",
        tags=["Menu"],

        description="Update one or more fields of an existing menu item.",
    ),
    destroy=extend_schema(
        summary="Delete a Menu Item", description="Remove a menu item from the system.",
        tags=["Menu"],
    ),
)
class MenuViewset(ModelViewSet):
    """ViewSet for managing Menu items.

    Provides endpoints for listing, retrieving, creating, updating, and deleting menu items.
    """

    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    lookup_field = "item_id"
    filter_backends = [DjangoFilterBackend]
    search_fields = ["title"]
    filterset_class = ProductFilter
    permission_classes = [IsAuthenticated]  

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
