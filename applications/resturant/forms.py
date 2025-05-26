from datetime import datetime

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Field, Layout, Row, Submit
from django import forms


class MenuFilterFormHelper(forms.Form):
    """Form helper for filtering menu items in the restaurant application.

    Provides a user-friendly interface for filtering menu items by price, inventory, and product name.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "get"

        self.fields["min_price"].label = "Minimum Price"
        self.fields["max_price"].label = "Maximum Price"
        self.fields["inventory"].label = "Inventory"
        self.fields["title"].label = "Product Name"
        self.helper.layout = Layout(
            Row(
                Column(Field("min_price"), css_class="col-4 "),
                Column(Field("max_price"), css_class="col-4 "),
                Column(Field("inventory"), css_class="col-4 "),
                css_class="row form-group",
            ),
            Row(
                Column(Field("title"), css_class="col-12 form-control"), css_class="row"
            ),
            Row(
                Column(
                    Submit(
                        name="Filter Results",
                        value="Filter Menu",
                        css_class="btn btn-success col-12",
                    ),
                    css_class="col-12 form-control",
                ),
                css_class="row d-grid gap-2",
            ),
        )


class BookingFilterFormHelper(forms.Form):
    """Form helper for filtering restaurant bookings.

    Allows users to filter bookings by date, time, party size, and booking party name.
    """

    date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "get"
        self.fields["min_no_of_guests"].label = "Minimum Party Size"
        self.fields["max_no_of_guests"].label = "Maximum Party Size"
        self.fields["date"].label = "Reservation Date"
        self.fields["name"].label = "Booking Party Name"
        self.fields["time"].label = "Reservation Time"
        self.helper.layout = Layout(
            Row(
                Column(Field("min_no_of_guests"), css_class="col-6"),
                Column(Field("max_no_of_guests"), css_class="col-6 "),
                css_class="row form-group",
            ),
            Row(
                Column(
                    Field("date", attrs={"input_type": "date"}),
                    value=datetime.now().date,
                    css_class="col-6",
                ),
                Column(Field("time", attrs={"input_type": "time"}), css_class="col-6 "),
                css_class="row form-group",
            ),
            Row(
                Column(
                    Field("name"), value="Larry Lemon", css_class="col-12 form-control"
                ),
                css_class="row",
            ),
            Row(
                Column(
                    Submit(
                        name="Filter Bookings",
                        value="Filter Bookings",
                        css_class="btn btn-success col-12",
                    ),
                    css_class="col-12",
                ),
                css_class="row d-grid gap-2",
            ),
        )
