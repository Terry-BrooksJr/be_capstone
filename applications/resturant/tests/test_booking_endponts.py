import datetime

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from applications.resturant.models import Booking


class BookingsViewsetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.test_user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.test_token = Token.objects.create(user=self.test_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.test_token.key}")
        self.list_url = reverse("bookings-list")
        self.valid_booking_data = {
            "name": "Alice Smith",
            "no_of_guests": 2,
            "date": f"{(datetime.datetime.now().date()+datetime.timedelta(days=5)).strftime('%m-%d-%Y')}",  # Current date + 5 days
            "time": "07:00 PM",
            "booking_id": 55,
        }
        self.invalid_booking_data = {
            "name": "",
            "no_of_guests": 0,
            "date": "invalid-date",
            "time": "invalid-time",
        }
        # Create a booking instance for retrieval, update, and deletion tests
        self.booking = Booking.objects.create(
            name="Bob Johnson",
            no_of_guests=4,
            date=datetime.datetime(2024, 5, 20, 18, 30),
        )
        self.detail_url = reverse("bookings-detail", args=[self.booking.booking_id])

    def test_create_booking_with_valid_data(self):
        response = self.client.post(
            path=reverse("bookings-create"),
            data=self.valid_booking_data,
            format="json",
            headers={"Authorization": f"Token {self.test_token.key}"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 2)
        self.assertEqual(Booking.objects.latest("booking_id").name, "Alice Smith")

    def test_create_booking_with_invalid_data(self):
        response = self.client.post(
            reverse("bookings-create"), self.invalid_booking_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_booking(self):
        response = self.client.get(self.detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("name"), self.booking.name)

    def test_update_booking(self):
        updated_data = {
            "name": "Bob Johnson Jr.",
            "no_of_guests": 5,
            "date": f"{(datetime.datetime.now().date()+datetime.timedelta(days=5)).strftime('%m-%d-%Y')}",
            "time": "08:00 PM",
        }
        response = self.client.put(self.detail_url, updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.name, "Bob Johnson Jr.")
        self.assertEqual(self.booking.no_of_guests, 5)
        self.assertEqual(
            self.booking.date.strftime("%m-%d-%Y %I:%M %p"),
            datetime.datetime.combine(
                (datetime.datetime.now().date() + datetime.timedelta(days=5)),
                datetime.time(20, 0),
            ).strftime("%m-%d-%Y %I:%M %p"),
        )

    def test_partial_update_booking(self):
        partial_data = {"no_of_guests": 6}
        response = self.client.patch(self.detail_url, partial_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.no_of_guests, 6)
        self.assertEqual(
            self.booking.name, self.booking.name
        )  # Name should remain unchanged

    def test_delete_booking(self):
        response = self.client.delete(self.detail_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Booking.objects.filter(booking_id=self.booking.booking_id).exists()
        )

    def test_list_bookings(self):
        response = self.client.get(self.list_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.json()["results"], list)
        self.assertGreaterEqual(len(response.json()), 1)

    def test_retrieve_nonexistent_booking(self):
        non_existent_url = reverse("bookings-detail", args=[9999])
        response = self.client.get(non_existent_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
