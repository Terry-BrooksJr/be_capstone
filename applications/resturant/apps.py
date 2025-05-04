import applications.resturant
from django.apps import AppConfig


class ResturantConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "applications.resturant"

    def ready(self):
        import applications.resturant.schema