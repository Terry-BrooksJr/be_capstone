# Create your tests here.
from django.http import HttpResponse
from django.test import Client, TestCase, override_settings

# You may need to adjust the import path for the middleware and settings


def testing_unprotected(request):
    return HttpResponse("This is an unprotected view.", status=200)


def testing_protected(request):
    return HttpResponse("This is a protected view.", status=200)


class BytePatrolAccessTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Example: set up allowed and disallowed IPs
        self.allowed_ip = "192.168.1.1"
        self.disallowed_ip = "10.0.0.1"
        # Example protected and unprotected paths
        self.protected_path = "/byte_patrol/protected/"
        self.unprotected_path = "/byte_patrol/public/"

    @override_settings(BYTE_PATROL_ALLOWED_IPS=["192.168.1.1"])
    def test_allowed_ip_access_protected_path(self):
        response = self.client.get(self.protected_path, REMOTE_ADDR=self.allowed_ip)
        self.assertNotEqual(
            response.status_code, 403, "Allowed IP should access protected path"
        )

    @override_settings(BYTE_PATROL_ALLOWED_IPS=["192.168.1.1"])
    def test_disallowed_ip_access_protected_path(self):
        response = self.client.get(self.protected_path, REMOTE_ADDR=self.disallowed_ip)
        self.assertEqual(
            response.status_code, 403, "Disallowed IP should not access protected path"
        )

    @override_settings(BYTE_PATROL_ALLOWED_IPS=["192.168.1.1"])
    def test_allowed_ip_access_unprotected_path(self):
        response = self.client.get(self.unprotected_path, REMOTE_ADDR=self.allowed_ip)
        self.assertNotEqual(
            response.status_code, 403, "Allowed IP should access unprotected path"
        )

    @override_settings(BYTE_PATROL_ALLOWED_IPS=["192.168.1.1"])
    def test_disallowed_ip_access_unprotected_path(self):
        response = self.client.get(
            self.unprotected_path, REMOTE_ADDR=self.disallowed_ip
        )
        self.assertNotEqual(
            response.status_code, 403, "Disallowed IP should access unprotected path"
        )
