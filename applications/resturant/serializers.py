from datetime import datetime

from rest_framework import serializers
from resturant.models import Booking, Menu


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = "__all__"


class BookingSerializer(serializers.ModelSerializer):

    booking_id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255, min_length=5, allow_null=False)
    no_of_guests = serializers.IntegerField(min_value=1, max_value=25)
    date = serializers.DateField(format="%m-%d-%Y", input_formats="%m-%d-%Y")
    time = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["time"] = representation["date"].strftime("%I:%M %p")
        representation["date"] = representation["date"].strftime("%m-%d-%Y")
        return representation

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        parsed_time = datetime.strptime(data["time"], "%I:%M %p")
        parsed_date = datetime.strptime(data["date"], "%m-%d-%Y")
        data["date"] = datetime.combine(parsed_date, parsed_time)
        return data

    def get_time(self, obj):
        return obj.date.strftime("%I:%M %p")
