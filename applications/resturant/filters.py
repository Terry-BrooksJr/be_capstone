from django_filters import CharFilter, DateFilter, FilterSet, NumberFilter, TimeFilter

from applications.resturant.forms import BookingFilterFormHelper, MenuFilterFormHelper
from applications.resturant.models import Booking, Menu


class ProductFilter(FilterSet):
    """FilterSet for filtering Menu objects.

    Allows filtering by minimum price, maximum price, title (case-insensitive contains), and minimum inventory.
    """

    min_price = NumberFilter(field_name="price", lookup_expr="gte")
    max_price = NumberFilter(field_name="price", lookup_expr="lte")
    title = CharFilter(field_name="title", lookup_expr="icontains")
    inventory = NumberFilter(field_name="inventory", lookup_expr="gte")

    class Meta:
        model = Menu
        fields = ["min_price", "max_price", "title", "inventory"]
        exclude = ["item_id"]
        form = MenuFilterFormHelper


class BookingFilter(FilterSet):
    """FilterSet for filtering Booking objects.

    Allows filtering by date, number of guests, and name (case-insensitive contains).
    """

    date = DateFilter(field_name="date")
    time = TimeFilter(field_name="time")
    min_no_of_guests = NumberFilter(field_name="no_of_guests", lookup_expr="gte")
    max_no_of_guests = NumberFilter(field_name="no_of_guests", lookup_expr="lte")
    name = CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Booking
        fields = ["date", "min_no_of_guests", "max_no_of_guests", "name", "time"]
        form = BookingFilterFormHelper
        exclude = ["booking_id"]
