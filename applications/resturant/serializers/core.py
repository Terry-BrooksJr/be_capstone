from cProfile import label
from datetime import datetime
from re import M

from django.forms import model_to_dict
from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema_field,
    extend_schema_serializer,
)
from rest_framework import serializers, status
from rest_framework.validators import UniqueTogetherValidator

from applications.resturant.models import Booking, Menu

from django.contrib.auth.models import User
from loguru  import logger

def validate_date_in_future(value):
        """Check if the booking date is in the future.

        Args:
            booking_date (datetime): The date of the booking

        Returns:
            bool: True if the booking date is in the future, False otherwise
        """
        if not value > datetime.now():
            raise serializers.ValidationError("Booking date must be in the future.")
class CustomUserSerializer(serializers.ModelSerializer):

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
class BookingRequestSerializer(serializers.ModelSerializer):
    """Serializer for Booking objects used in requests.
    Serializes and deserializes booking data, handling date and time formatting.
    """
    name = serializers.CharField(
        max_length=255,
        min_length=5,
        allow_null=False,
        help_text="Name of the person making the booking (minimum 5 characters)",
    ),
    no_of_guests = serializers.IntegerField(
        min_value=1,
        max_value=25,
        help_text="Number of guests in the booking (between 1 and 25)",
    ),
    date = serializers.DateField(
        format="%m-%d-%YT%h:%MZ",
        input_formats=["%m-%d-%Y"],
        help_text="Date of the booking in MM-DD-YYYY format",
    ),
    time = serializers.SerializerMethodField(
        initial=datetime.now().strftime("%I:%M %p"),
        help_text="Time of the booking in 12-hour format (e.g., '07:30 PM')"
        
    )
    
    def get_time(self, obj):
        """Formats the time portion of the date field into a human-readable time.

        Returns:
            str: Time in 12-hour format with AM/PM indicator (e.g., '07:30 PM')
        """
        return obj.date.strftime("%I:%M %p")

    time = serializers.SerializerMethodField(
        help_text="Time of the booking in 12-hour format (e.g., '07:30 PM')"
    )

    class Meta:
        model = Booking
        fields = ( "name", "no_of_guests", "date", "time")
        
class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking objects."""
    booking_id = serializers.IntegerField(
        read_only=True, help_text="Unique identifier for the booking"
    )
    name = serializers.CharField(
        label="Reservation Name",
        max_length=255,
        min_length=5,
        allow_null=False,
        help_text="Name of the person making the booking (minimum 5 characters)",
    )
    no_of_guests = serializers.IntegerField(
        label="Number of Guests",
        min_value=1,
        max_value=25,
        help_text="Number of guests in the booking (between 1 and 25)",
    )
    date = serializers.DateField(
        label="Booking Date",
        input_formats=["%Y-%m-%d", "iso-8601", "%m-%d-%Y"],
        help_text="Date of the booking in YYYY-MM-DD format",
        validators=[ validate_date_in_future,
        ]
    )
    time = serializers.TimeField(
        label="Booking Time",
        input_formats=["hh:mm [AM|PM]","%I:%M %p", "%I:%M%p" ],
        initial=datetime.now().strftime("%I:%M %p"),
        help_text="Time of the booking in 12-hour format (e.g., '07:30 PM')",
    )
    class Meta:
        model = Booking
        fields = ("booking_id", "name", "no_of_guests", "date", "time")
        validators = [
            UniqueTogetherValidator(
                queryset=Booking.objects.all(),
                fields=['name', 'date'],
                message="A booking with this name for this date already exists."
            )
        ]

    def to_representation(self, instance):
        """Convert model instance to JSON serializable format.

        Formats date and time into specified formats.

        Args:
            instance: The model instance to serialize

        Returns:
            dict: The serialized representation
        """
        # representation = super().to_representation(instance)
        representation = model_to_dict(instance)
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

        time_str = data.get("time")
        date_str = data.get("date")

            if not time_str:
                raise serializers.ValidationError({"time": "This field is required."})
            if not date_str:
                raise serializers.ValidationError({"date": "This field is required."})

            try:
                    parsed_time = datetime.strptime(time_str, "%I:%M %p")
            except (ValueError, TypeError):
                parsed_time = datetime.strptime(time_str, "%I:%M%p")
            except Exception as e:
                    raise serializers.ValidationError({
                        "time":
                        "Time must be in the format 'HH:MM AM/PM' (e.g., '07:30 PM')."
                    }) from e

            try:
                    parsed_date = datetime.strptime(date_str, "%m-%d-%Y")
                    if parsed_date < datetime.now():
                        raise serializers.ValidationError({
                            "date": "Booking date must be in the future."
                        })
            except (ValueError, TypeError) as exc:
                    raise serializers.ValidationError({
                        "date":
                        "Date must be in the format 'MM-DD-YYYY' (e.g., '12-31-2024')."
                    }) from exc

            data["date"] = datetime.combine(parsed_date.date(), parsed_time.time())
            del(data["time"])
            return data

class BookingResponseSerializer(serializers.ModelSerializer):
    """Serializer for Booking objects.

    Serializes and deserializes booking data, handling date and time formatting.
    """

    booking_id = serializers.IntegerField(
        read_only=True, help_text="Unique identifier for the booking"
    )
    name = serializers.CharField(
        label="Reservation Name",
        max_length=255,
        min_length=5,
        allow_null=False,
        help_text="Name of the person making the booking (minimum 5 characters)",
    )
    no_of_guests = serializers.IntegerField(
        label="Number of Guests",
        min_value=1,
        max_value=25,
        help_text="Number of guests in the booking (between 1 and 25)",
        required=True
    )
    date = serializers.DateField(
        label= "Reservation Date and Time",
        format="%m-%d-%YT%h:%MZ",
        help_text="Date of the booking in MM-DD-YYYY format",
    )


    class Meta:
        model = Booking
        fields = ("booking_id", "name", "no_of_guests", "date")

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

