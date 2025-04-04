# Create your views here.
from django.views.generic import TemplateView
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from resturant.models import Booking, Menu
from resturant.serializers import BookingSerializer, MenuSerializer


class Index(TemplateView):
    template_name = "index.html"


@extend_schema_view(
    list=extend_schema(
        summary="List All Current Bookings",
        description="Retrieve a list of all Little Lemon Bookings in the system.",
        auth=None,
        parameters=None,
        tags=["Bookings"],
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
                               "time": "3:45 PM"
                           },
                                            {
                               "booking_id": 125, 
                               "name": "Jane Doe", 
                               "no_of_guests": 8,
                               "date": "01-02-1970",
                               "time": "5:45 PM"
                           }, 
                           ],
                status_codes=[status.HTTP_200_OK],
            )
        ],
    ),
    retrieve=extend_schema(
        summary="Retrieve Specific Booking By ID",
        auth=None,
        tags=["Bookings"],
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
                               "time": "3:45 PM"
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
        description="Create a new booking entry. All fields are required in the request payload.",
        request=BookingSerializer,
        auth=None,
        responses=BookingSerializer,
        examples=[
            OpenApiExample(
                "Create Booking Example",
                description="Example payload for creating a booking",
                value={"name": "John Doe", "no_of_guests": 4, "date": "2025-04-03"},
                response_only=False,
                status_codes=[status.HTTP_201_CREATED],
            )
        ],
    ),
    update=extend_schema(
        summary="Update a Book", description="Update all details of an existing book."
    ),
    partial_update=extend_schema(
        summary="Partial Update of a Book",
        description="Update one or more fields of an existing book.",
    ),
    destroy=extend_schema(
        summary="Delete a Book", description="Remove a book from the system."
    ),
)
class BookingsViewset(ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer


class MenuViewset(ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
