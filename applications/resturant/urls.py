from django.urls import path
from applications.resturant import endpoints
urlpatterns = [
    path("/", endpoints.Index.as_view(), name='index')
]
