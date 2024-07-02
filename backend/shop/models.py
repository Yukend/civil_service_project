from django.db import models
from user.models import User

from .constants import *


class ShopType(models.Model):
    """
    choices class for material type
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)


class Shop(models.Model):
    """
    Shop model class
    mapped by : User - many to one mapping
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    type = models.ManyToManyField(ShopType, related_name=SHOPS, db_table=SHOP_MATERIAL)
    invented_year = models.IntegerField()
    email = models.CharField(max_length=100, null=True)
    telephone = models.CharField(max_length=15, blank=True, null=True)
    mobile = models.BigIntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True, related_name=CREATE_SHOP
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True, related_name=UPDATE_SHOP
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name=SHOPS, null=True
    )
    is_deleted = models.BooleanField(editable=False, default=False)
