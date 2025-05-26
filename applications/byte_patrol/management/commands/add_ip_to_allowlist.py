from byte_patrol.middleware import IPRestrictionMiddleware
from byte_patrol.models import IPAllowList
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Add an IP address to the allow list"

    def add_arguments(self, parser):
        parser.add_argument("ip_address", type=str, help="IP address to add")
        parser.add_argument("--description", type=str, help="Description for this IP")

    def handle(self, *args, **options):
        ip_address = options["ip_address"]
        description = options.get("description", "")

        # Try to find existing entry
        ip_entry, created = IPAllowList.objects.update_or_create(
            ip_address=ip_address,
            defaults={"description": description, "is_active": True},
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f"Successfully added {ip_address} to the allow list")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Updated existing entry for {ip_address}")
            )

        # Invalidate cache
        IPRestrictionMiddleware().invalidate_cache()
