# Register your models here.
from django.contrib import admin

from applications.resturant.models import Booking, Menu

admin.site.register(Menu)
admin.site.register(Booking)
