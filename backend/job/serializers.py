import datetime
import re

from rest_framework import serializers

from .models import Job
from .my_logger import logger


class JobSerializer(serializers.ModelSerializer):
    """
    User serializer class for validate inputs from request
    """

    class Meta:
        model = Job
        fields = "__all__"

    def validate(self, data):
        if not re.match("[0-9]{,3}", str(data["number_of_workers"])):
            logger.error("Number of workers must be integer.")
            raise serializers.ValidationError(
                "Number of workers must be integer.",
            )
        if not re.match("[0-9]{,3}", str(data["working_days"])):
            logger.error("Working days must be integer.")
            raise serializers.ValidationError(
                "Working days must be integer.",
            )
        if not data["work_date"] > datetime.date.today():
            logger.error("Work must be starts to after 24 hours from now.")
            raise serializers.ValidationError(
                "Work must be starts to after 24 hours from now.",
            )
        if data["work_pay"] > 2000:
            logger.error("Work pay must be numbers and max pay was 2000.")
            raise serializers.ValidationError(
                "Work pay must be numbers and max pay was 2000.",
            )
        return data


class JobResponseSerializer(serializers.ModelSerializer):
    """
    User serializer class for validate inputs from request
    """

    class Meta:
        model = Job
        fields = (
            "work_type",
            "number_of_workers",
            "work_date",
            "working_days",
            "work_pay",
        )
