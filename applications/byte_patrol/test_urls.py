from django.http import HttpResponse
from django.urls import path


def testing_unprotected(request):
    return HttpResponse("This is an unprotected view.", status=200)


def testing_protected(request):
    return HttpResponse("This is a protected view.", status=200)


# Set up test URLs for BytePatrol tests
urlpatterns = [
    path("byte_patrol/protected/", testing_protected, name="protected"),
    path("byte_patrol/public/", testing_unprotected, name="unprotected"),
]
