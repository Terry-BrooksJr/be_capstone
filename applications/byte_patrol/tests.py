# Create your tests here.
import logging
import os
import sys

from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.test.client import ClientHandler, RequestFactory
from loguru import logger

from applications.byte_patrol.test_urls import testing_protected, testing_unprotected

from .middleware import IPRestrictionMiddleware

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class CustomClientHandler(ClientHandler):
    """
    Custom ClientHandler that ensures middleware is properly initialized and processed.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Ensure middleware is loaded correctly
        logger.debug("CustomClientHandler initialized with middleware:")
        if self._middleware_chain:
            for middleware in self._middleware_chain:
                logger.debug(f"  - {middleware.__class__.__name__}")
    def load_middleware(self):
        """Override load_middleware to ensure middleware is properly initialized"""
        super().load_middleware()
        logger.debug("Middleware loaded in CustomClientHandler:")
        for middleware in self._middleware_chain:
            logger.debug(f"  - {middleware.__class__.__name__}")

    def get_response(self, request):
        """Override to add debugging around middleware processing"""
        logger.debug(f"\nProcessing request with CustomClientHandler: {request.path}")
        logger.debug(f"Request META: {request.META}")

        # Call each middleware in the chain directly to debug
        logger.debug("Calling each middleware individually:")
        for middleware in self._middleware_chain:
            logger.debug(f"  Calling {middleware.__class__.__name__}")
            try:
                # Try calling middleware directly
                response = middleware(request)
                logger.debug(
                    f"  Response from {middleware.__class__.__name__}: {response.status_code if response else 'None'}"
                )

                # If the middleware returned a response, return it immediately
                if response:
                    logger.debug(
                        f"  Early response from {middleware.__class__.__name__}: {response.status_code}"
                    )
                    return response
            except Exception as e:
                logger.debug(f"  Error calling {middleware.__class__.__name__}: {e}")

        # If we get here, no middleware returned a response, call the chain normally
        try:
            response = super().get_response(request)
            logger.debug(f"Response from middleware chain: {response.status_code}")
            return response
        except Exception as e:
            logger.debug(f"Error in middleware chain: {e}")
            raise


# Custom test client that uses our custom handler
class CustomClient(Client):
    """Custom test client that uses our CustomClientHandler"""

    def __init__(self, *args, **kwargs):
        handler = CustomClientHandler()
        super().__init__(handler, *args, **kwargs)


class BytePatrolAccessTests(TestCase):
    # Use our custom client
    client_class = CustomClient

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Enable debug logging
        logging.basicConfig(level=logging.DEBUG)

    def setUp(self):
        # Custom client is automatically created by TestCase due to client_class
        # Example: set up allowed and disallowed IPs
        self.allowed_ip = "192.168.1.1"
        self.disallowed_ip = "10.0.0.1"
        # Example protected and unprotected paths
        self.protected_path = "/byte_patrol/protected/"  # Must match pattern exactly
        self.unprotected_path = "/byte_patrol/public/"

    @override_settings(
        BYTE_PATROL_ALLOWED_IPS=["192.168.1.1"],
        BYTE_PATROL_PROTECTED_PATHS=[
            r"^/byte_patrol/protected/$",
            r"^/byte_patrol/protected/.*$",
        ],
        ROOT_URLCONF="applications.byte_patrol.test_urls",
        MIDDLEWARE=[
            "applications.byte_patrol.middleware.IPRestrictionMiddleware",  # Put our middleware first
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ],
    )
    def test_allowed_ip_access_protected_path(self):
        response = self.client.get(self.protected_path, REMOTE_ADDR=self.allowed_ip)
        self.assertNotEqual(
            response.status_code, 403, "Allowed IP should access protected path"
        )

    @override_settings(
        BYTE_PATROL_ALLOWED_IPS=["192.168.1.1"],
        BYTE_PATROL_PROTECTED_PATHS=[
            r"^/byte_patrol/protected/$"
        ],  # Simplified pattern
        BYTE_PATROL_CACHE_TIMEOUT=0,  # Disable caching for tests
        ROOT_URLCONF="applications.byte_patrol.test_urls",
        MIDDLEWARE=[
            "applications.byte_patrol.middleware.IPRestrictionMiddleware",  # Put our middleware first
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ],
    )
    def test_disallowed_ip_access_protected_path(self):
        # Debug the current settings and middleware state
        logger.debug(
            f"Test settings - BYTE_PATROL_ALLOWED_IPS: {getattr(settings, 'BYTE_PATROL_ALLOWED_IPS', None)}"
        )
        logger.debug(
            f"Test settings - BYTE_PATROL_PROTECTED_PATHS: {getattr(settings, 'BYTE_PATROL_PROTECTED_PATHS', None)}"
        )
        logger.debug(
            f"Test settings - MIDDLEWARE: {getattr(settings, 'MIDDLEWARE', None)}"
        )

        # Verify our middleware is in the middleware stack
        middleware_path = "applications.byte_patrol.middleware.IPRestrictionMiddleware"
        self.assertIn(
            middleware_path,
            settings.MIDDLEWARE,
            f"The middleware {middleware_path} is not in the middleware stack",
        )

        # Create a proper get_response function that simulates the next middleware in the chain
        def get_response(request):
            # This simulates what would happen if the request passes through all middleware
            if request.path == self.protected_path:
                return testing_protected(request)
            return testing_unprotected(request)

        # Create a middleware instance for testing with the proper get_response
        middleware = IPRestrictionMiddleware(get_response)

        # Check if the path is actually restricted by the middleware
        is_restricted = middleware._is_path_restricted(self.protected_path)
        logger.debug(f"Is path '{self.protected_path}' restricted? {is_restricted}")

        # Test each path variant against the pattern to debug matching issues
        import re

        pattern = r"^/byte_patrol/protected/$"
        match1 = bool(re.match(pattern, self.protected_path))
        match2 = bool(re.match(pattern, self.protected_path.lstrip("/")))
        logger.debug(f"Direct regex match with pattern '{pattern}':")
        logger.debug(f"  - Path: '{self.protected_path}', Match: {match1}")
        logger.debug(
            f"  - Path without leading slash: '{self.protected_path.lstrip('/')}', Match: {match2}"
        )

        # Check if the test IP is allowed
        is_allowed = middleware._is_ip_allowed(self.disallowed_ip)
        logger.debug(f"Is IP '{self.disallowed_ip}' allowed? {is_allowed}")

        # Verify the key assumptions before making the request
        self.assertTrue(is_restricted, "The path should be recognized as restricted")
        self.assertTrue(
            match1, f"The pattern '{pattern}' should match path '{self.protected_path}'"
        )
        self.assertFalse(is_allowed, "The IP should not be recognized as allowed")

        # Test the middleware's _get_client_ip method directly
        logger.debug("Testing middleware _get_client_ip method directly...")
        factory = RequestFactory()
        mock_request1 = factory.get(self.protected_path)
        mock_request1.META["REMOTE_ADDR"] = self.disallowed_ip
        client_ip1 = middleware._get_client_ip(mock_request1)
        logger.debug(f"Client IP from REMOTE_ADDR: {client_ip1}")
        self.assertEqual(
            client_ip1,
            self.disallowed_ip,
            "Client IP should be correctly extracted from REMOTE_ADDR",
        )

        # Test with X-Forwarded-For
        mock_request2 = factory.get(self.protected_path)
        mock_request2.META["HTTP_X_FORWARDED_FOR"] = self.disallowed_ip
        client_ip2 = middleware._get_client_ip(mock_request2)
        logger.debug(f"Client IP from HTTP_X_FORWARDED_FOR: {client_ip2}")
        self.assertEqual(
            client_ip2,
            self.disallowed_ip,
            "Client IP should be correctly extracted from HTTP_X_FORWARDED_FOR",
        )

        # Test the middleware process_request method directly
        logger.debug("Testing middleware process_request method directly...")
        mock_request = factory.get(self.protected_path)
        mock_request.META["REMOTE_ADDR"] = self.disallowed_ip

        # Call the middleware directly (this will call both process_request and get_response)
        direct_response = middleware(mock_request)
        logger.debug(f"Direct middleware response: {direct_response}")
        logger.debug(
            f"Direct middleware response status code: {direct_response.status_code if direct_response else 'None'}"
        )

        # Verify the middleware returns a 403 response directly
        self.assertIsNotNone(
            direct_response, "Middleware should return a response for disallowed IP"
        )
        self.assertEqual(
            direct_response.status_code,
            403,
            "Middleware should return 403 for disallowed IP",
        )

        # Also test process_request directly to verify it's producing the expected response
        process_request_response = middleware.process_request(mock_request)
        logger.debug(f"process_request response: {process_request_response}")
        logger.debug(
            f"process_request status code: {process_request_response.status_code if process_request_response else 'None'}"
        )
        self.assertIsNotNone(
            process_request_response,
            "process_request should return a response for disallowed IP",
        )
        self.assertEqual(
            process_request_response.status_code,
            403,
            "process_request should return 403 for disallowed IP",
        )

        # Now make the real request with both REMOTE_ADDR and HTTP_X_FORWARDED_FOR
        logger.debug(
            "\nMaking real request with both REMOTE_ADDR and HTTP_X_FORWARDED_FOR..."
        )
        logger.debug(f"Using middleware from settings: {settings.MIDDLEWARE}")

        # Add custom middleware to capture the client IP during the real request
        original_process_request = middleware.process_request

        def debug_process_request(request):
            client_ip = middleware._get_client_ip(request)
            logger.debug(f"Real request client IP detected: {client_ip}")
            logger.debug(
                f"REMOTE_ADDR in real request: {request.META.get('REMOTE_ADDR')}"
            )
            logger.debug(
                f"HTTP_X_FORWARDED_FOR in real request: {request.META.get('HTTP_X_FORWARDED_FOR')}"
            )
            return original_process_request(request)

        # Temporarily replace the middleware's process_request method
        middleware.process_request = debug_process_request

        # Make the request with explicit HTTP headers
        logger.debug("Using custom test client to make request...")
        self.client.handler._middleware_chain  # Access to trigger debug logger.debug

        response = self.client.get(
            self.protected_path,
            REMOTE_ADDR=self.disallowed_ip,
            HTTP_X_FORWARDED_FOR=self.disallowed_ip,
            # Force all headers to be passed to request.META
            enforce_csrf_checks=False,
        )

        # Restore the original process_request method
        middleware.process_request = original_process_request

        # Debug the response
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.content}")
        logger.debug(
            f"Response headers: {response._headers if hasattr(response, '_headers') else 'No headers'}"
        )

        # Check if the URL is configured correctly in URLconf
        from django.urls import Resolver404, resolve

        try:
            match = resolve(self.protected_path)
            logger.debug(f"URL resolved to: {match.func.__name__} at {match.url_name}")
        except Resolver404:
            logger.debug(f"URL {self.protected_path} could not be resolved!")

        # Add a simplified test just using RequestFactory directly
        logger.debug("\nTrying with RequestFactory directly...")
        factory = RequestFactory()
        req = factory.get(self.protected_path)
        req.META["REMOTE_ADDR"] = self.disallowed_ip

        # Get the actual middleware instance from the client handler
        middleware_found = False
        for middleware in self.client.handler._middleware_chain:
            if isinstance(middleware, IPRestrictionMiddleware):
                middleware_found = True
                logger.debug(f"Found IPRestrictionMiddleware in client handler")
                direct_response = middleware(req)
                logger.debug(
                    f"Direct response from client middleware: {direct_response.status_code if direct_response else 'None'}"
                )

        self.assertTrue(
            middleware_found, "IPRestrictionMiddleware should be in the client handler"
        )

        self.assertEqual(
            response.status_code, 403, "Disallowed IP should not access protected path"
        )

    @override_settings(
        BYTE_PATROL_ALLOWED_IPS=["192.168.1.1"],
        ROOT_URLCONF="applications.byte_patrol.test_urls",
        MIDDLEWARE=[
            "applications.byte_patrol.middleware.IPRestrictionMiddleware",  # Put our middleware first
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ],
    )
    def test_allowed_ip_access_unprotected_path(self):
        response = self.client.get(self.unprotected_path, REMOTE_ADDR=self.allowed_ip)
        self.assertNotEqual(
            response.status_code, 403, "Allowed IP should access unprotected path"
        )

    @override_settings(
        BYTE_PATROL_ALLOWED_IPS=["192.168.1.1"],
        ROOT_URLCONF="applications.byte_patrol.test_urls",
        MIDDLEWARE=[
            "applications.byte_patrol.middleware.IPRestrictionMiddleware",  # Put our middleware first
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ],
    )
    def test_disallowed_ip_access_unprotected_path(self):
        response = self.client.get(
            self.unprotected_path, REMOTE_ADDR=self.disallowed_ip
        )
        self.assertNotEqual(
            response.status_code, 403, "Disallowed IP should access unprotected path"
        )
