from django.db.models import Index, Model, fields


class Booking(Model):
    booking_id = fields.SmallAutoField(verbose_name="Booking ID", primary_key=True)
    name = fields.CharField(
        verbose_name="Guest Name", max_length=255, null=False, blank=False
    )
    no_of_guests = fields.PositiveSmallIntegerField(
        verbose_name="Party Size", blank=False, null=False
    )
    date = fields.DateTimeField(verbose_name="Date of Booking")
    def __str__(self):
        return f"Booking ID: {self.booking_id}, Name: {self.name}, Date: {self.date}"
        
    class Meta:
        app_label = "resturant"
        db_table = "bookings"
        ordering = ["-date"]
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        managed = True
        indexes = [
            Index(fields=["name"], name="idx_name"),      
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
    def __str__(self):
        return f"Menu Item ID: {self.item_id}, Title: {self.title}, Price: {self.price}, Inventory: {self.inventory}"
    class Meta:
        app_label = "resturant"
        db_table = "inventory"
        ordering = ["title"]
        verbose_name = "Menu Item"
        verbose_name_plural = "Menu Items"
        managed = True
        indexes = [
            Index(fields=["price"], name="idx_price"),
            Index(fields=["price", "inventory"], name="idx_price_inventory"),
            Index(fields=["title"], name="idx_title"),
            Index(fields=["title", "inventory"], name="idx_title_inventory"),
        ]
