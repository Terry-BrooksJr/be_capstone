import datetime as DT
from datetime import datetime
from typing import Any, Dict, Union

from django.http import QueryDict
from django.utils.timezone import now as TIMEZONE_AWARE_NOW
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


def validate_date_in_future(
    value: DT.datetime,
) -> Union[None, serializers.ValidationError]:
    """Check if the booking date is in the future.

    Args:
        booking_date (datetime): The date of the booking

    Returns:
        bool: True if the booking date is in the future, False otherwise
    """
    if not value > TIMEZONE_AWARE_NOW():
        raise serializers.ValidationError("Booking date must be in the future.")


def party_size_validator(value: int) -> Union[None, serializers.ValidationError]:
    """Check if the party size is within the allowed range.

    Args:
        value (int): The number of guests in the booking

    Returns:
        None

    Raises:
        serializers.ValidationError: If the party size is not between 1 and 25
    """
    if not 1 <= value <= 25:
        raise serializers.ValidationError("Party size must be between 1 and 25.")


def price_is_valid(value: float) -> Union[None, serializers.ValidationError]:
    """Check if the price is a positive number.
    Args:
        value (float): The price of the menu item
    """
    if value <= 0:
        raise serializers.ValidationError("Price must be a positive number.")


def inventory_is_valid(value: int) -> Union[None, serializers.ValidationError]:
    """Check if the inventory is a non-negative number.
    Args:
        value (int): The inventory quantity of the menu item
    """
    if value < 0:
        raise serializers.ValidationError("Inventory must be a non-negative number.")


class DateTimeParsingMixin:
    def parse_datetime_fields(self, data, request):
        """Parses and validates date and time fields from input data.

        Ensures date and time are present, valid, and in the future, then combines them into a datetime object.

        Args:
            data: The input data containing date and time fields.
            request: The HTTP request object.

        Returns:
            dict: The updated data with a combined datetime object in the 'date' field.

        Raises:
            serializers.ValidationError: If date or time are missing or invalid.
        """
        logger.debug(f"Raw data before datetime parsing: {data}")

        if isinstance(data, QueryDict):
            data: Dict[str, Any] = self._parse_querydict(data)

        date_str = data.get("date")
        time_str = data.get("time")
        if request is not None and (
            request.method != "PATCH" and (not date_str or not time_str)
        ):
            raise serializers.ValidationError(
                {"date/time": "Both date and time are required."}
            )

        parsed_time = self._parse_time(time_str)
        parsed_date = self._parse_date(date_str)
        logger.debug(f"Parsed date: {parsed_date}, {type(parsed_date)}")
        logger.debug(f"Parsed time: {parsed_time}, {type(parsed_time)}")

        combined = datetime.combine(parsed_date, parsed_time)
        logger.debug(f"Parsed combined datetime: {combined}, {type(combined)}")
        logger.debug(
            f"Timezone-aware now: {TIMEZONE_AWARE_NOW()}, {type(TIMEZONE_AWARE_NOW())}"
        )
        current_time = TIMEZONE_AWARE_NOW()
        if combined < current_time:
            raise serializers.ValidationError({"date": "Date must be in the future."})
        # Check if the serializer aexpects a date or datetime for the 'date' field
        date_field = self.fields.get("date", None)
        if date_field is not None and hasattr(date_field, "to_internal_value"):

            if isinstance(date_field, serializers.DateField):
                # If the field expects a date, store only the date part
                data["date"] = combined.date()
            elif isinstance(date_field, serializers.DateTimeField):
                # If the field expects a datetime, store the full datetime
                data["date"] = combined
            else:
                raise serializers.ValidationError(
                    {"date": "Unsupported field type for 'date'."}
                )
        else:
            data["date"] = combined

        data.pop("time", None)
        data.pop("csrfmiddlewaretoken", None)
        return data

    def _parse_querydict(self, input_dict: QueryDict) -> dict:
        """Converts a QueryDict to a standard dict and formats the time field.
        Extracts and formats the time from the date field in the QueryDict.

        Args:
            data: The QueryDict containing date and time information.

        Returns:
            dict: A standard dictionary with a formatted 'time' field.
        """
        data = input_dict.dict()
        data["time"] = (
            datetime.strptime(data["date"], "%Y-%m-%dT%H:%M")  # noqa
            .time()
            .strftime("%I:%M %p")
        )
        return data

    def _parse_time(self, time_str: str) -> DT.time:
        """Parses a time string into a time object.

        Converts a string in 12-hour format with AM/PM into a Python time object. Raises a validation error if the format is invalid.

        Args:
            time_str: The time string to parse.

        Returns:
            datetime.time: The parsed time object.

        Raises:
            serializers.ValidationError: If the time string is not in a valid format.
        """
        try:
            return (
                time_str.time()
                if isinstance(time_str, DT.datetime)
                else DT.datetime.strptime(time_str, "%I:%M %p").time()
            )
        except (ValueError, TypeError):
            try:
                return datetime.strptime(time_str, "%I:%M%p").time()
            except Exception as e:
                raise serializers.ValidationError(
                    {"time": "Time must be in the format 'HH:MM AM/PM'."}
                ) from e

    def _parse_date(self, date_str: str):
        """Parses a date string into a date object.

        Accepts multiple date formats and returns a Python date object. Raises a validation error if the format is invalid.

        Args:
            date_str: The date string to parse.

        Returns:
            datetime.date: The parsed date object.

        Raises:
            serializers.ValidationError: If the date string is not in a valid format.
        """
        if isinstance(date_str, DT.date):
            logger.debug(f"Date is already a date object: {date_str}")
            return date_str
        try:
            return datetime.strptime(date_str, "%m-%d-%Y").date()
        except (ValueError, TypeError):
            try:
                return datetime.strptime(date_str, "%Y-%m-%dT%H:%M").date()
            except (ValueError, TypeError):
                try:
                    return datetime.strptime(date_str, "%Y-%m-%d").date()
                except Exception as e:
                    raise serializers.ValidationError(
                        {
                            "date": "Date must be in format 'MM-DD-YYYY' or 'YYYY-MM-DDTHH:MM'"
                        }
                    ) from e


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
        max_digits=6,
        decimal_places=2,
        help_text="Price of the menu item in USD",
        validators=[price_is_valid],
    )
    inventory = serializers.IntegerField(
        help_text="Current available quantity of the item",
        validators=[inventory_is_valid],
    )

    class Meta:
        model = Menu
        fields = "__all__"


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
        validators=[
            party_size_validator,
        ],
        error_messages={
            "min_value": "Party size must be at least 1.",
            "max_value": "Party size must not exceed 25.",
        },
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

    @extend_schema_field(OpenApiTypes.TIME,"time")
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
