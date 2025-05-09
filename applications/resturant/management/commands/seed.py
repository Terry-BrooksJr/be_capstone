import json

from django.core.management.base import BaseCommand

from applications.models import Booking, Menu
from mock.data import bookings, menu


def seed_bookings():
    """Seeds the Booking table with sample data."""
    booking_objects = []
    for booking in bookings:
        json.loads(booking)
        booking_objects.append(
            Booking(
                name=booking.name,
                no_of_guests=booking.no_of_guests,
                booking_date=booking.booking_date,
            )
        )
    Booking.objects.bulk_create(bookings_objects)
    print("Bookings seeded successfully!")
    return True


def seed_menu():
    """Seeds the Menu table with sample data."""
    menu_items_objects = []
    for item in menu:
        json.loads(item)
        menu_items_objects.append(
            Menu(title=item.title, price=item.price, inventory=item.inventory)
        )
    Menu.objects.bulk_create(menu_items_objects)
    print("Menu seeded successfully!")
    return True


def seed_all():
    """Seeds all tables with sample data."""
    if seed_bookings() and seed_menu():
        print("All data seeded successfully!")
        return True
    else:
        print("Failed to seed data!")
        return False


class Command(BaseCommand):
    help = "Seeds the database with sample data"
    requires_migrations_checks = True
    output_transaction = True

    def handle(self, *args, **options):
        if options["no-bookings"]:
            seed_menu
        elif options["no-menu"]:
            seed_bookings()
        else:
            seed_all()

    def add_arguments(self, parser):
        """Adds command line arguments for seeding the database."""
        parser.add_argument(
            "--no-bookings",
            action="store_true",
            help="Seeds the Booking table with sample data",
        )
        parser.add_argument(
            "--no-menu",
            action="store_true",
            help="Seeds the Menu table with sample data",
        )
