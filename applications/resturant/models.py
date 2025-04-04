# Create your models here.
from django.db.models import Index, Model, fields


class Booking(Model):
    booking_id = fields.SmallAutoField(verbose_name="Booking ID", primary_key=True)
    name = fields.CharField(
        verbose_name="Guest Name", max_length=255, null=False, blank=False
    )
    no_of_guests = fields.PositiveSmallIntegerField(
        verbose_name="Party Size", blank=False, null=True
    )
    date = fields.DateField(verbose_name="Date of Booking")

    class Meta:
        db_table = "bookings"
        ordering = ["-date"]
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        managed = True
        indexes = [
            Index(fields=["date"], name="idx_date"),
        ]


class Menu(Model):
    item_id = fields.SmallAutoField(verbose_name="Menu Item ID", primary_key=True)
    title = fields.CharField(
        verbose_name="Item Title", max_length=255, null=False, blank=False
    )
    price = fields.DecimalField(
        verbose_name="Item Price ($USD)", max_digits=10, decimal_places=2
    )
    inventory = fields.PositiveSmallIntegerField(
        verbose_name="Number in Stock", blank=False, null=True
    )

    class Meta:
        db_table = "inventory"
        ordering = ["title"]
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"
        managed = True
        indexes = [
            Index(fields=["price"], name="idx_price"),
            Index(fields=["price", "inventory"], name="idx_price_inventory"),
        ]
