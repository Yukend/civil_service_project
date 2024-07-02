from material_stock.my_logger import logger
from rest_framework import serializers
from user.models import User

from .models import Profession


class ProfessionSerializer(serializers.ModelSerializer):
    """
    User serializer class for validate inputs from request
    """

    class Meta:
        model = Profession
        fields = "__all__"

    def validate(self, data):
        if not data["work_experience"] < 40:
            logger.error("Work_experience must be less than 40 years.")
            raise serializers.ValidationError(
                "Work_experience must be less than 40 years.",
            )
        if not data["expected_salary"] < 2000:
            logger.error(
                "Your expected salary to high please enter salary less than 2000."
            )
            raise serializers.ValidationError(
                "Your expected salary to high please enter salary less than 2000.",
            )
        return data


class ProfessionResponseSerializer(serializers.ModelSerializer):
    """
    Profession serializer for return response we can hide some important details
    """

    class UserResponseSerializer(serializers.ModelSerializer):
        """
        User serializer for return response we can hide some important details
        """

        class Meta:
            model = User
            fields = ("name", "email", "mobile")

    user = UserResponseSerializer()

    class Meta:
        model = Profession
        fields = ("user", "profession", "work_experience", "expected_salary", "gender")
