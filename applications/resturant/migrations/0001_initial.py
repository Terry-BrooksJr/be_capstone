# Generated by Django 5.2 on 2025-04-03 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Booking",
            fields=[
                (
                    "date",
                    models.DateField(auto_created=True, verbose_name="Date of Booking"),
                ),
                (
                    "booking_id",
                    models.SmallAutoField(
                        primary_key=True, serialize=False, verbose_name="Booking ID"
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="Guest Name")),
                (
                    "no_of_guests",
                    models.PositiveSmallIntegerField(
                        null=True, verbose_name="Party Size"
                    ),
                ),
            ],
            options={
                "verbose_name": "Booking",
                "verbose_name_plural": "Bookings",
                "db_table": "bookings",
                "ordering": ["-date"],
                "managed": True,
                "indexes": [models.Index(fields=["date"], name="idx_date")],
            },
        ),
        migrations.CreateModel(
            name="Menu",
            fields=[
                (
                    "item_id",
                    models.SmallAutoField(
                        primary_key=True, serialize=False, verbose_name="Menu Item ID"
                    ),
                ),
                ("title", models.CharField(max_length=255, verbose_name="Item Title")),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        verbose_name="Item Price ($USD)",
                    ),
                ),
                (
                    "inventory",
                    models.PositiveSmallIntegerField(
                        null=True, verbose_name="Number in Stock"
                    ),
                ),
            ],
            options={
                "verbose_name": "Menu Item",
                "verbose_name_plural": "Menu Items",
                "db_table": "inventory",
                "ordering": ["title"],
                "managed": True,
                "indexes": [
                    models.Index(fields=["price"], name="idx_price"),
                    models.Index(
                        fields=["price", "inventory"], name="idx_price_inventory"
                    ),
                ],
            },
        ),
    ]
