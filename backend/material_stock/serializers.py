import re

from rest_framework import serializers

from .models import MaterialStock
from .my_logger import logger


class MaterialStockSerializer(serializers.ModelSerializer):
    """
    User serializer class for validate inputs from request
    """

    class Meta:
        model = MaterialStock
        fields = "__all__"

    def validate(self, data):
        if not re.match("[A-Za-z\s]+", data["name"]):
            logger.error("Name must be characters.")
            raise serializers.ValidationError(
                "Name must be characters.",
            )
        if not re.match("[0-9]+[\sA-Za-z]+", data["stock"]):
            logger.error("Stock must be number then follow character.")
            raise serializers.ValidationError(
                "Stock must be number then follow character.",
            )
        if not isinstance(data["rate"], float):
            logger.error("Name must be at least 10 characters long.")
            raise serializers.ValidationError(
                "Name must be at least 10 characters long.",
            )
        if not re.match("[A-Za-z\s]+", data["brand"]):
            logger.error("Brand name must be characters.")
            raise serializers.ValidationError(
                "Brand name must be characters.",
            )
        return data


class MaterialStockResponseSerializer(serializers.ModelSerializer):
    """
    Material stock serializer for return response we can hide some important details
    """

    class Meta:
        model = MaterialStock
        fields = ["type", "name", "stock", "rate", "brand"]
