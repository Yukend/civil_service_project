from django.db import models
from user.models import User

from .constants import *


class AddressType(models.Model):
    id = models.AutoField(primary_key=True)
    address_type = models.CharField(max_length=100, default=USER_ADDRESS)


class Address(models.Model):
    """
    Address model class
    mapped by : User model - many to one mapping
    """

    id = models.AutoField(primary_key=True)
    building_number = models.CharField(max_length=5, null=True, blank=True)
    street = models.CharField(max_length=100, null=True, blank=True)
    village_area = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100)
    landmark = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name=CREATE_SHOP_ADDRESS,
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name=UPDATE_SHOP_ADDRESS,
    )
    module = models.ForeignKey(
        AddressType, on_delete=models.CASCADE, related_name=ADDRESS_MODULE
    )
    module_field_id = models.IntegerField(null=True)
    is_deleted = models.BooleanField(editable=False, default=False)
