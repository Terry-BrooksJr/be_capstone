from django.test import TestCase
from resturant.serializers.core import BookingSerializer
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from applications.resturant.models import Booking
from loguru import logger 
from django.contrib.auth.models import User
import datetime
from rest_framework.authtoken.models import Token
from mock.data import booking

class BookingSerializerRepresentationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.test_user = User.objects.create_user(username='testuser', password='testpassword')
        self.test_token = Token.objects.create(user=self.test_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.test_token.key}')
        self.booking =  Booking.objects.create(
            name="John Doe", no_of_guests=4, date=datetime.datetime(2024, 5, 10, 18, 30)
        )
    def test_to_representation_formats_date_and_time(self):
        # Arrange


        # Act
        serializer = BookingSerializer(self.booking)
        data = serializer.data

        # Assert
        self.assertEqual(data["date"], "05-10-2024")
        self.assertEqual(data["time"], "06:30 PM")

    def test_to_internal_value_parses_date_and_time(self):
        # Arrange
        input_data = {
            "name": "Jane Doe",
            "no_of_guests": 3,
            "date": f"{(datetime.datetime.now().date()+datetime.timedelta(days=5)).strftime('%m-%d-%Y')}", # Current date in MM-DD-YYYY format
            "time": "07:45 PM",
        }

        # Act
        serializer:BookingSerializer = BookingSerializer(data=input_data)
        is_valid = serializer.is_valid()
        self.assertTrue(is_valid)
        logger.debug(serializer.validated_data)
        
        # Assert
        parsed_datetime = serializer.validated_data.get("date")
        self.assertEqual(parsed_datetime.year, (datetime.datetime.now() + datetime.timedelta(days=5)).year)
        self.assertEqual(parsed_datetime.month, (datetime.datetime.now() + datetime.timedelta(days=5)).month)
        self.assertEqual(parsed_datetime.day, (datetime.datetime.now() + datetime.timedelta(days=5)).day)


    def test_to_internal_value_invalid_date(self):
        # Arrange
        input_data = {
            "name": "Jane Doe",
            "no_of_guests": 3,
            "date": "invalid-date",
            "time": "07:45 PM",
        }

        # Act
        serializer = BookingSerializer(data=input_data)

        # Assert
        self.assertFalse(serializer.is_valid())
        self.assertIn("date", serializer.errors)

    def test_to_internal_value_invalid_time(self):
        # Arrange
        input_data = {
            "name": "Jane Doe",
            "no_of_guests": 3,
            "date": "05-20-2024",
            "time": "invalid-time",
        }

        # Act
        serializer = BookingSerializer(data=input_data)

        # Assert
        self.assertFalse(serializer.is_valid())
        self.assertIn("date", serializer.errors)


    def test_to_internal_value_missing_date(self):
         # Arrange
        input_data = {
            "name": "Jane Doe",
            "no_of_guests": 3,
            "time": "07:45 PM",
        }

        # Act
        serializer = BookingSerializer(data=input_data)

        # Assert
        self.assertFalse(serializer.is_valid())
        self.assertIn("date", serializer.errors)

    def test_to_internal_value_missing_time(self):
         # Arrange
        input_data = {
            "name": "Jane Doe",
            "no_of_guests": 3,
            "date": "05-20-2024",
        }

        # Act
        serializer = BookingSerializer(data=input_data)

        # Assert
        self.assertFalse(serializer.is_valid())
        self.assertIn("date", serializer.errors)