from django.test import TestCase, RequestFactory
from django.http import JsonResponse

# Your view (can be removed if just used for testing)
def secure_check_view(request):
    return JsonResponse({
        'is_secure': request.is_secure(),
        'X-Forwarded-Proto': request.META.get('HTTP_X_FORWARDED_PROTO'),
    })

class SecureRequestTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_secure_proxy_ssl_header(self):
        # Simulate a request with X-Forwarded-Proto set to 'https'
        request = self.factory.get('/', HTTP_X_FORWARDED_PROTO='https')

        # Add wsgi.url_scheme manually (RequestFactory doesn't simulate full WSGI)
        request.META['wsgi.url_scheme'] = 'http'  # Default scheme before proxy

        # Now call the view
        response = secure_check_view(request)
        data = response.json()

        # Assertions
        assert data['X-Forwarded-Proto'] == 'https', "X-Forwarded-Proto header not set correctly"
        assert data['is_secure'] is True, "Request not marked as secure despite header"
