from datetime import datetime

from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema_field,
    extend_schema_serializer,
)
from rest_framework import serializers, status

from applications.resturant.models import Booking, Menu

from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):

    def __getitem__(self, key):
        return super().__getitem__(key)
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']
        
@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Successful Menu POST Example",
            value={
                "title": "Greek Salad",
                "price": 12.99,
                "inventory": 100,
            },
            request_only=True,
            response_only=False,
            status_codes=[status.HTTP_201_CREATED],
        ),
        OpenApiExample(
            "Successful Menu  GET Example",
            value={
                "item_id": 1,
                "title": "Greek Salad",
                "price": 12.99,
                "inventory": 100,
            },
            request_only=False,
            response_only=True,
            status_codes=[status.HTTP_200_OK],
        ),
    ]
)
class MenuSerializer(serializers.ModelSerializer):
    """Serializer for Menu objects.

    Serializes and deserializes menu item data.
    """

    item_id = serializers.IntegerField(
        read_only=True, help_text="Unique identifier for the menu item"
    )
    title = serializers.CharField(max_length=255, help_text="Name of the menu item")
    price = serializers.DecimalField(
        max_digits=6, decimal_places=2, help_text="Price of the menu item in USD"
    )
    inventory = serializers.IntegerField(
        help_text="Current available quantity of the item"
    )

    class Meta:
        model = Menu
        fields = "__all__"


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Booking Example",
            value={
                "booking_id": 123,
                "name": "John Doe",
                "no_of_guests": 4,
                "date": "04-15-2025",
                "time": "07:30 PM",
            },
            request_only=False,
            response_only=False,
        )
    ]
)
class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking objects.

    Serializes and deserializes booking data, handling date and time formatting.
    """

    booking_id = serializers.IntegerField(
        read_only=True, help_text="Unique identifier for the booking"
    )
    name = serializers.CharField(
        max_length=255,
        min_length=5,
        allow_null=False,
        help_text="Name of the person making the booking (minimum 5 characters)",
    )
    no_of_guests = serializers.IntegerField(
        min_value=1,
        max_value=25,
        help_text="Number of guests in the booking (between 1 and 25)",
    )
    date = serializers.SerializerMethodField(
        help_text="Date of the booking in 'MM-DD-YYYY' format"
    )
    
    
    time = serializers.SerializerMethodField(
        help_text="Time of the booking in 12-hour format (e.g., '07:30 PM')"
    )
    @extend_schema_field(serializers.CharField())
    def get_date(self, obj):
        return obj.date.date() if isinstance(obj.date, datetime) else obj.date
    
    @extend_schema_field(serializers.CharField())
    def get_time(self, obj):
        """Formats the time portion of the date field into a human-readable time.

        Returns:
            str: Time in 12-hour format with AM/PM indicator (e.g., '07:30 PM')
        """
        return obj.date.strftime("%I:%M %p")

    class Meta:
        model = Booking
        fields = ("booking_id", "name", "no_of_guests", "date", "time")

    def to_representation(self, instance):
        """Convert model instance to JSON serializable format.

        Formats date and time into specified formats.

        Args:
            instance: The model instance to serialize

        Returns:
            dict: The serialized representation
        """
        representation = super().to_representation(instance)
        representation["time"] = instance.date.strftime("%I:%M %p")
        representation["date"] = instance.date.strftime("%m-%d-%Y")
        return representation

    def to_internal_value(self, data):
        """Convert primitive data types to model field values.

        Parses date and time strings into datetime objects.

        Args:
            data: The data to deserialize

        Returns:
            dict: The deserialized values
        """
        data = super().to_internal_value(data)
        parsed_time = datetime.strptime(data["time"], "%I:%M %p")
        parsed_date = datetime.strptime(data["date"], "%m-%d-%Y")
        data["date"] = datetime.combine(parsed_date.date(), parsed_time.time())
        return data
