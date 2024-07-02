import re
from hashlib import md5

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import User, Verification
from .my_logger import logger


class UserSerializer(serializers.ModelSerializer):
    """
    User serializer class for validate inputs from request
    """

    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        if len(data["username"]) < 10:
            logger.error("Username must be at least 10 characters long.")
            raise serializers.ValidationError(
                "Username must be at least 10 characters long.",
            )
        if len(data["password"]) < 8:
            logger.error("Password must be at least 6 to 15 characters long.")
            raise serializers.ValidationError(
                "Password must be at least 8 characters long.",
            )
        if not re.match("[A-Za-z\s]+", data["name"]):
            logger.error("Name must be at least 10 characters long.")
            raise serializers.ValidationError(
                "Name must be at least 10 characters long.",
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

    @staticmethod
    def validate_password(value: str) -> str:
        """
        Hash value passed by user.

        :param value: password of a user
        :return: a hashed version of the password
        """
        return md5(value.encode()).hexdigest()


class UserResponseSerializer(serializers.ModelSerializer):
    """
    User serializer for return response we can hide some important details
    """

    class Meta:
        model = User
        fields = ("username", "name", "email", "mobile", "role")


class VerificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Verification
        fields = "__all__"
