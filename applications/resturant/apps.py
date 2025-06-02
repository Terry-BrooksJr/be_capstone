from django.apps import AppConfig

from utils.logging import setup_loguru


class ResturantConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "applications.resturant"

    def ready(self):
        setup_loguru()
