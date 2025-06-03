import json

from django.http import JsonResponse
from django.test import RequestFactory, TestCase


# Simple test-only view to check secure status
def secure_check_view(request):
    return JsonResponse(
        {
            "is_secure": request.is_secure(),
            "X-Forwarded-Proto": request.META.get("HTTP_X_FORWARDED_PROTO"),
        }
    )


class SecureRequestTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def parse_json_response(self, response):
        return json.loads(response.content.decode("utf-8"))

    def test_is_secure_with_https_forwarded_proto(self):
        request = self.factory.get("/", HTTP_X_FORWARDED_PROTO="https")
        request.META["wsgi.url_scheme"] = "http"
        response = secure_check_view(request)
        data = self.parse_json_response(response)

        self.assertEqual(data["X-Forwarded-Proto"], "https")
        self.assertTrue(
            data["is_secure"], msg="Expected secure request with 'https' header"
        )

    def test_is_secure_with_no_forwarded_proto(self):
        request = self.factory.get("/")
        request.META["wsgi.url_scheme"] = "http"
        response = secure_check_view(request)
        data = self.parse_json_response(response)

        self.assertIsNone(data["X-Forwarded-Proto"])
        self.assertFalse(
            data["is_secure"],
            msg="Expected insecure request without X-Forwarded-Proto header",
        )

    def test_is_secure_with_http_forwarded_proto(self):
        request = self.factory.get("/", HTTP_X_FORWARDED_PROTO="http")
        request.META["wsgi.url_scheme"] = "http"
        response = secure_check_view(request)
        data = self.parse_json_response(response)

        self.assertEqual(data["X-Forwarded-Proto"], "http")
        self.assertFalse(
            data["is_secure"],
            msg="Expected insecure request with 'http' in X-Forwarded-Proto",
        )

    def test_is_secure_with_invalid_forwarded_proto(self):
        request = self.factory.get("/", HTTP_X_FORWARDED_PROTO="ftp")
        request.META["wsgi.url_scheme"] = "http"
        response = secure_check_view(request)
        data = self.parse_json_response(response)

        self.assertEqual(data["X-Forwarded-Proto"], "ftp")
        self.assertFalse(
            data["is_secure"], msg="Expected insecure request with invalid scheme 'ftp'"
        )
