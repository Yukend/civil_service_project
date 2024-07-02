import datetime
import re

from django.core.validators import validate_email
from material_stock.my_logger import logger
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from user.serializers import UserResponseSerializer

from .models import Shop


class ShopSerializer(serializers.ModelSerializer):
    """
    User serializer class for validate inputs from request
    """

    class Meta:
        model = Shop
        fields = "__all__"

    def validate(self, data):
        if not re.match("[A-Za-z\s]+", data["name"]):
            logger.error("Shop name must be at characters.")
            raise serializers.ValidationError(
                "Shop name must be at characters.",
            )
        if not int(datetime.date.today().year) >= data["invented_year"]:
            logger.error("Please enter valid year.")
            raise serializers.ValidationError(
                "Please enter valid year.",
            )
        if data["telephone"] == "":
            return None
        elif not re.match("(?:\+\d{2})?\d{3,4}\D?\d{3}\D?\d{3}", data["telephone"]):
            logger.error("Enter valid telephone number.")
            raise serializers.ValidationError(
                "Enter valid telephone number.",
            )
        if not re.match("(?:\+\d{2})?\d{3,4}\D?\d{3}\D?\d{3}", str(data["mobile"])):
            logger.error("Enter valid mobile number.")
            raise serializers.ValidationError(
                "Enter valid mobile number.",
            )
        try:
            validate_email(data["email"])
        except ValidationError:
            logger.error("Invalid email format.")
            raise serializers.ValidationError("Invalid email format.")
        return data


class ShopResponseSerializer(serializers.ModelSerializer):
    """
    Shop serializer for return response we can hide some important details
    """

    user = UserResponseSerializer()

    class Meta:
        model = Shop
        fields = ("name", "user", "telephone", "mobile", "email", "invented_year")
