from datetime import datetime

from django.test import TestCase
from resturant.serializers.core import BookingSerializer

from applications.resturant.models import Booking


class BookingSerializerRepresentationTest(TestCase):
    def test_to_representation_formats_date_and_time(self):
        # Arrange
        booking = Booking.objects.create(
            name="John Doe", no_of_guests=4, date=datetime(2024, 5, 10, 18, 30)
        )

        # Act
        serializer = BookingSerializer(booking)
        data = serializer.data

        # Assert
        self.assertEqual(data["date"], "05-10-2024")
        self.assertEqual(data["time"], "06:30 PM")

    def test_to_internal_value_parses_date_and_time(self):
        # Arrange
        input_data = {
            "name": "Jane Doe",
            "no_of_guests": 3,
            "date": "05-20-2024",
            "time": "07:45 PM",
        }

        # Act
        serializer = BookingSerializer(data=input_data)
        is_valid = serializer.is_valid()

        # Assert
        self.assertTrue(is_valid)
        parsed_datetime = serializer.validated_data["date"]
        self.assertEqual(parsed_datetime.year, 2024)
        self.assertEqual(parsed_datetime.month, 5)
        self.assertEqual(parsed_datetime.day, 20)
        self.assertEqual(parsed_datetime.hour, 19)


#         self.assertEqual(parsed_datetime.minute, 45)

# class BookingViewSetTests(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.booking_list_url = reverse("booking-list")

#     def test_create_booking_valid_and_invalid_cases(self):
#         """Test creating bookings with various valid, edge, and invalid data"""
#         test_cases = [
#             # Happy path
#             ({"name": "John Doe", "no_of_guests": 2, "date": "2024-05-03T8:00"}, status.HTTP_201_CREATED),
#             ({"name": "Jane Doe", "no_of_guests": 4, "date": "2024-06-15", "time": "19:30"}, status.HTTP_201_CREATED),
#             # Edge cases
#             ({"name": "John Doe", "no_of_guests": 1, "date": "2024-05-03", "time": "23:59"}, status.HTTP_201_CREATED),
#             ({"name": "Jane Doe", "no_of_guests": 10, "date": "2024-06-15", "time": "00:00"}, status.HTTP_201_CREATED),
#             # Error cases
#             ({"name": "", "no_of_guests": 2, "date": "2024-05-03", "time": "18:00"}, status.HTTP_400_BAD_REQUEST),
#             ({"no_of_guests": 2, "date": "2024-05-03", "time": "18:00"}, status.HTTP_400_BAD_REQUEST),
#             ({"name": "John Doe", "no_of_guests": 0, "date": "2024-05-03", "time": "18:00"}, status.HTTP_400_BAD_REQUEST),
#             ({"name": "John Doe", "no_of_guests": 2, "date": "invalid-date", "time": "18:00"}, status.HTTP_400_BAD_REQUEST),
#         ]

#         for booking_data, expected_status in test_cases:
#             with self.subTest(booking_data=booking_data):
#                 response = self.client.post(self.booking_list_url, booking_data, format="json")
#                 self.assertEqual(response.status_code, expected_status)

# def test_list_bookings(self):
#     """Test listing all bookings"""
#     Booking.objects.create(name="Existing Booking 1", no_of_guests=2, date="2024-05-03T12:00:00Z")
#     Booking.objects.create(name="Existing Booking 2", no_of_guests=4, date="2024-06-10T18:00:00Z")

#     response = self.client.get(self.booking_list_url)
#     self.assertEqual(response.status_code, status.HTTP_200_OK)

#     bookings = Booking.objects.all()
#     serializer = BookingSerializer(bookings, many=True)
#     self.assertEqual(response.data, serializer.data)

# def test_retrieve_booking_success(self):
#     """Test retrieving an existing booking"""
#     booking = Booking.objects.create(id=1, name="Test Booking", no_of_guests=2, date="2024-07-20", time="17:00")

#     url = reverse("booking-detail", kwargs={"pk": booking.id})
#     response = self.client.get(url)
#     self.assertEqual(response.status_code, status.HTTP_200_OK)
#     self.assertEqual(response.data, {
#         "name": booking.name,
#         "no_of_guests": booking.no_of_guests,
#         "date": str(booking.date),
#         "time": booking.time.strftime("%H:%M")
#     })

# def test_retrieve_booking_not_found(self):
#     """Test retrieving a non-existent booking"""
#     url = reverse("booking-detail", kwargs={"pk": 2})
#     response = self.client.get(url)
#     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
