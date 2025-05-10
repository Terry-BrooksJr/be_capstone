from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from applications.resturant.models import Menu


class MenuViewsetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.test_user = User.objects.create_user(
            username="menu_testuser", password="testpassword"
        )
        self.test_token = Token.objects.create(user=self.test_user)
        self.menu_list_url = reverse("menu-list")
        self.menu_create_url = reverse("menu-create")
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.test_token.key}")

        self.valid_menu_data = {
            "title": "Greek Salad",
            "price": "12.99",
            "inventory": 100,
        }

        self.invalid_menu_data = {
            "title": "",
            "price": "",
            "inventory": "",
        }

        self.menu = Menu.objects.create(title="Tacos", price=5.99, inventory=30)
        self.menu_detail_url = reverse("menu-detail", args=[self.menu.pk])

    def test_list_menu(self):
        response = self.client.get(self.menu_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_menu_with_valid_data(self):
        response = self.client.post(self.menu_create_url, self.valid_menu_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["title"], "Greek Salad")

    def test_create_menu_with_invalid_data(self):
        # Invalid: missing required field 'title'
        invalid_data_missing_title = {"price": 10.99, "inventory": 10}
        response = self.client.post(self.menu_create_url, invalid_data_missing_title)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid: negative price
        invalid_data_negative_price = {
            "title": "Negative Price",
            "price": -5.00,
            "inventory": 10,
        }
        response = self.client.post(self.menu_create_url, invalid_data_negative_price)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid: non-numeric price
        invalid_data_non_numeric_price = {
            "title": "Non-numeric Price",
            "price": "ten dollars",
            "inventory": 10,
        }
        response = self.client.post(
            self.menu_create_url, invalid_data_non_numeric_price
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid: negative inventory
        invalid_data_negative_inventory = {
            "title": "Negative Inventory",
            "price": 10.99,
            "inventory": -3,
        }
        response = self.client.post(
            self.menu_create_url, invalid_data_negative_inventory
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid: missing required field 'price'
        invalid_data_missing_price = {"title": "No Price", "inventory": 10}
        response = self.client.post(self.menu_create_url, invalid_data_missing_price)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Invalid: missing required field 'inventory'
        invalid_data_missing_inventory = {"title": "No Inventory", "price": 10.99}
        response = self.client.post(
            self.menu_create_url, invalid_data_missing_inventory
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Existing invalid data test
        response = self.client.post(self.menu_create_url, self.invalid_menu_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_menu(self):
        response = self.client.get(self.menu_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["title"], self.menu.title)

    def test_update_menu(self):
        response = self.client.patch(self.menu_detail_url, {"inventory": 50})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["inventory"], 50)

    def test_delete_menu(self):
        response = self.client.delete(self.menu_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
