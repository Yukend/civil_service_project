import re

from rest_framework import serializers

from .models import Address
from .my_logger import logger


class AddressSerializer(serializers.ModelSerializer):
    """
    User serializer class for validate inputs from request
    """

    class Meta:
        model = Address
        fields = "__all__"

    def validate(self, data):
        if data["building_number"] == "":
            return None
        elif not re.match("[A-Za-z-/0-9]+", data["building_number"]):
            logger.error("Building number must be character, numbers and -/ only .")
            raise serializers.ValidationError(
                "Building number must be character, numbers and -/ only .",
            )
        if data["street"] == "":
            return None
        elif not re.match("[A-Za-z\s]+", data["street"]):
            logger.error("Street name must be characters.")
            raise serializers.ValidationError(
                "Street name must be characters.",
            )
        if not re.match("[A-Za-z\s]+", data["district"]):
            logger.error("district name must be characters.")
            raise serializers.ValidationError(
                "district name must be characters.",
            )
        if not re.match("[A-Za-z\s]+", data["village_area"]):
            logger.error("Village name must be characters.")
            raise serializers.ValidationError(
                "Village name must be characters.",
            )
        if not re.match("[A-Za-z\s]+", data["city"]):
            logger.error("City name must be characters.")
            raise serializers.ValidationError(
                "City name must be characters.",
            )
        if not re.match("[A-Za-z\s]+", data["landmark"]):
            logger.error("Landmark must be characters.")
            raise serializers.ValidationError(
                "Landmark must be characters.",
            )
        if not re.match("[A-Za-z\s]+", data["state"]):
            logger.error("State name must be characters.")
            raise serializers.ValidationError(
                "State name must be characters.",
            )
        if not re.match("[0-9]{6}", str(data["pincode"])):
            logger.error("Pincode is to long or to low it must be six numbers.")
            raise serializers.ValidationError(
                "Pincode is to long or to low it must be six numbers.",
            )
        return data


class UserAddressResponseSerializer(serializers.ModelSerializer):
    """
    Address serializer for return response we can hide some important details
    """

    class Meta:
        model = Address
        fields = (
            "building_number",
            "street",
            "village_area",
            "landmark",
            "city",
            "district",
            "state",
            "pincode",
        )


class ShopAddressResponseSerializer(serializers.ModelSerializer):
    """
    Shop Address serializer for return response we can hide some important details
    """

    class Meta:
        model = Address
        fields = (
            "building_number",
            "street",
            "village_area",
            "landmark",
            "city",
            "district",
            "state",
            "pincode",
        )


class WorkingAddressResponseSerializer(serializers.ModelSerializer):
    """
    Working Address serializer for return response we can hide some important details
    """

    class Meta:
        model = Address
        fields = (
            "village_area",
            "landmark",
            "city",
            "district",
            "state",
            "pincode",
        )
