from django.urls import path

from applications.byte_patrol.tests import testing_protected, testing_unprotected

urlpatterns = [
    path("protected/", testing_protected, name="byte_patrol_protected"),
    path("public/", testing_unprotected, name="byte_patrol_public"),
]
