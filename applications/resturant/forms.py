from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import StrictButton
from crispy_forms.layout import Field, Layout, Div, Column, Row, HTML, Submit
from django import forms
from django_filters.fields import RangeField
from applications.resturant.models import Menu, Booking

class MenuFilterFormHelper(forms.Form):
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
                Column(
                    Field("min_price"), css_class="col-4 "), 
                Column(
                    Field("max_price"), css_class="col-4 "), 
                Column(
                    Field("inventory"), css_class="col-4 "),
                css_class="row form-group"),
            Row(        
                Column(
                    Field("title"), css_class="col-12 form-control"),
                css_class="row"),
            Row(
                Column(
                    Submit(name="Filter Results", value="Filter", css_class="btn btn-primary"), css_class="col-12 form-control"),
                css_class="row d-grid gap-2"),
        )
    
class BookingFilterFormHelper(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = "get"
        self.fields["min_no_guests"].label = "Minimum Party Size"
        self.fields["max_no_guests"].label = "Maximum Party Size"
        self.fields["date"].label = "Reservation Date"
        self.fields["name"].label = "Booking Party Name"
        self.helper.layout = Layout(
            Row(
                Column(
                    Field("min_no_guests"), css_class="col-6"), 
                Column(
                    Field("max_no_guests"), css_class="col-6 "),  
                css_class="row form-group"),
                  Row(
                Column(
                    Field("min_no_guests"), css_class="col-6"), 
                Column(
                    Field("max_no_guests"), css_class="col-6 "),  
                css_class="row form-group"),
            Row(
                Column(
                    Submit(name="Filter Bookings", value="Filter Bookings", css_class="btn btn-primary"), css_class="col-12 form-control"),
                css_class="row d-grid gap-2"),
        )
        
        class Meta:
            model = Menu
            labels = {
                "min_price": "Minimum Price($USD)",
                "max_price": "Maximum Price($USD)",
                "inventory": "Inventory",
                "title": "Item Name",
            }
