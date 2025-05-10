import datetime as DT
from datetime import datetime

from django.contrib.auth.models import User
from django.http import QueryDict
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema_field,
    extend_schema_serializer,
)
from loguru import logger
from rest_framework import serializers, status
from rest_framework.validators import UniqueTogetherValidator

from applications.resturant.models import Booking, Menu


def validate_date_in_future(value):
    """Check if the booking date is in the future.

    Args:
        booking_date (datetime): The date of the booking

    Returns:
        bool: True if the booking date is in the future, False otherwise
    """

    if not value > datetime.now():
        raise serializers.ValidationError("Booking date must be in the future.")


import datetime as DT
from datetime import datetime

from django.http import QueryDict
from loguru import logger
from rest_framework import serializers


class DateTimeParsingMixin:
    def parse_datetime_fields(self, data, request):
        """Returns the time portion of the date field in a human-readable 12-hour format.

        Formats the time from the Booking object's date field as a string with AM/PM.

        Args:
            obj: The Booking instance containing the date field.

        Returns:
            str: Time in 12-hour format with AM/PM (e.g., '07:30 PM').
        """
        logger.debug(f"Raw data before datetime parsing: {data}")

        if isinstance(data, QueryDict):
            data = data.dict()
            data["time"] = (
                datetime.strptime(data["date"], "%Y-%m-%dT%H:%M")
                .time()
                .strftime("%I:%M %p")
            )

        date_str = data.get("date")
        time_str = data.get("time")
        if request is not None and (
            request.method != "PATCH" and (not date_str or not time_str)
        ):
            raise serializers.ValidationError(
                {"date/time": "Both date and time are required."}
            )

        # Handle multiple time formats
        try:
            parsed_time = (
                time_str.time()
                if isinstance(time_str, DT.datetime)
                else DT.datetime.strptime(time_str, "%I:%M %p").time()
            )
        except (ValueError, TypeError):
            try:
                parsed_time = datetime.strptime(time_str, "%I:%M%p").time()
            except Exception as e:
                raise serializers.ValidationError(
                    {"time": "Time must be in the format 'HH:MM AM/PM'."}
                ) from e

        # Handle multiple date formats
        if isinstance(date_str, DT.date):
            parsed_date = date_str
        else:
            try:
                parsed_date = datetime.strptime(date_str, "%m-%d-%Y")
            except Exception:
                try:
                    parsed_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M")
                except Exception as e:
                    raise serializers.ValidationError(
                        {
                            "date": "Date must be in format 'MM-DD-YYYY' or 'YYYY-MM-DDTHH:MM'"
                        }
                    ) from e

        if parsed_date < datetime.now():
            raise serializers.ValidationError({"date": "Date must be in the future."})

        combined = datetime.combine(parsed_date, parsed_time)
        logger.debug(f"Parsed combined datetime: {combined}")

        data["date"] = combined
        data.pop("time", None)
        data.pop("csrfmiddlewaretoken", None)
        return data


class CustomUserSerializer(serializers.ModelSerializer):

    def __getitem__(self, key):
        return super().__getitem__(key)

    class Meta:
        model = User
        fields = ["url", "username", "email", "groups"]


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


# @extend_schema_serializer(
#     examples=[
#         OpenApiExample(
#             "Booking Example",
#             value={
#                 "booking_id": 123,
#                 "name": "John Doe",
#                 "no_of_guests": 4,
#                 "date": "04-15-2025",
#                 "time": "07:30 PM",
#             },
#             request_only=False,
#             response_only=False,
#         )
#     ]
# )
# class BookingRequestSerializer(serializers.ModelSerializer):
#     """Serializer for Booking objects used in requests.
#     Serializes and deserializes booking data, handling date and time formatting.
#     """

#     name = (
#         serializers.CharField(
#             max_length=255,
#             min_length=5,
#             allow_null=False,
#             help_text="Name of the person making the booking (minimum 5 characters)",
#         ),
#     )
#     no_of_guests = (
#         serializers.IntegerField(
#             min_value=1,
#             max_value=25,
#             help_text="Number of guests in the booking (between 1 and 25)",
#         ),
#     )
#     date = (
#         serializers.SerializerMethodField(
#             help_text="Date of the booking in MM-DD-YYYY format",
#         ),
#     )
#     time = serializers.SerializerMethodField(
#         initial=datetime.now().strftime("%I:%M %p"),
#         help_text="Time of the booking in 12-hour format (e.g., '07:30 PM')",
#     )

#     def get_date(self, obj):
#         """Formats the date portion of the date field into a human-readable date."""
#         return obj.date.strftime("%m-%d-%Y")
#     def get_time(self, obj):
#         """Formats the time portion of the date field into a human-readable time.

#         Returns:
#             str: Time in 12-hour format with AM/PM indicator (e.g., '07:30 PM')
#         """
#         return obj.date.strftime("%I:%M %p")

#     time = serializers.SerializerMethodField(
#         help_text="Time of the booking in 12-hour format (e.g., '07:30 PM')"
#     )

#     class Meta:
#         model = Booking
#         fields = ("name", "no_of_guests", "date", "time")


class BookingSerializer(DateTimeParsingMixin, serializers.ModelSerializer):
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
    date = serializers.DateTimeField(
        label="Booking Date",
        input_formats=["%Y-%m-%d", "iso-8601", "%m-%d-%Y"],
        help_text="Date of the booking in YYYY-MM-DD format",
        validators=[
            validate_date_in_future,
        ],
    )
    time = serializers.SerializerMethodField(
        initial=datetime.now().strftime("%I:%M %p"),
        help_text="Time of the booking in 12-hour format (e.g., '07:30 PM')",
    )

    class Meta:
        model = Booking
        fields = ("booking_id", "name", "no_of_guests", "date", "time")
        validators = [
            UniqueTogetherValidator(
                queryset=Booking.objects.all(),
                fields=["name", "date"],
                message="A booking with this name for this date already exists.",
            )
        ]

    @extend_schema_field(OpenApiTypes.TIME)
    def get_time(self, obj):
        """Returns the time portion of the date field in a human-readable 12-hour format.

        Formats the time from the Booking object's date field as a string with AM/PM.

        Args:
            obj: The Booking instance containing the date field.

        Returns:
            str: Time in 12-hour format with AM/PM (e.g., '07:30 PM').
        """
        return obj.date.strftime("%I:%M %p")

    def to_representation(self, instance):
        """Convert model instance to JSON serializable format.

        Formats date and time into specified formats.

        Args:
            instance: The model instance to serialize

        Returns:
            dict: The serialized representation
        """
        representation = super().to_representation(instance)
        # representation = model_to_dict(instance)
        logger.debug(f"Representation Pre-Processing: {representation}")
        # Convert date and time to human-readable formats
        representation["time"] = instance.date.strftime("%I:%M %p")
        representation["date"] = instance.date.strftime("%m-%d-%Y")
        logger.debug(f"Representation Post-Processing: {representation}")
        return representation

    def to_internal_value(self, data):
        """Convert primitive data types to model field values.

        Parses date and time strings into datetime objects.

        Args:
            data: The data to deserialize

        Returns:
            dict: The deserialized values
        """
        request = self.context.get("request")
        if request is not None:
            logger.debug(f"Request: {request}")
            if (
                request.method != "PATCH"
                or "date" in data.keys()
                and "time" in data.keys()
            ):
                data = self.parse_datetime_fields(data, request)
                logger.debug(f"Parsed data: {data}")
        return super().to_internal_value(data)


# class BookingResponseSerializer(serializers.ModelSerializer):
#     """Serializer for Booking objects.

#     Serializes and deserializes booking data, handling date and time formatting.
#     """

#     booking_id = serializers.IntegerField(
#         read_only=True, help_text="Unique identifier for the booking"
#     )
#     name = serializers.CharField(
#         label="Reservation Name",
#         max_length=255,
#         min_length=5,
#         allow_null=False,
#         help_text="Name of the person making the booking (minimum 5 characters)",
#     )
#     no_of_guests = serializers.IntegerField(
#         label="Number of Guests",
#         min_value=1,
#         max_value=25,
#         help_text="Number of guests in the booking (between 1 and 25)",
#         required=True,
#     )
#     date = serializers.DateField(
#         label="Reservation Date and Time",
#         format="%m-%d-%YT%h:%MZ",
#         help_text="Date of the booking in MM-DD-YYYY format",
#     )

#     class Meta:
#         model = Booking
#         fields = ("booking_id", "name", "no_of_guests", "date")

#     def to_representation(self, instance):
#         """Convert model instance Qualityto JSON serializable format.

#         Formats date and time into specified formats.

#         Args:
#             instance: The model instance to serialize

#         Returns:
#             dict: The serialized representation
#         """
#         representation = super().to_representation(instance)
#         representation["time"] = instance.date.strftime("%I:%M %p")
#         representation["date"] = instance.date.strftime("%m-%d-%Y")
#         return representation
