from django.apps import AppConfig


class BytePatrolConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "byte_patrol"

    def ready(self):
        # Import signal handlers
        pass
