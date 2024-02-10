from django.db import models
from shop.models import Shop
from shop.models import ShopType
from user.models import User
from .constants import *


class MaterialStock(models.Model):
    """
    Material stock model class
    """

    id = models.AutoField(primary_key=True)
    type = models.ForeignKey(ShopType, on_delete=models.CASCADE, related_name=MATERIAL)
    name = models.CharField(max_length=100)
    stock = models.CharField(max_length=100)
    rate = models.FloatField(default=0.0)
    brand = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,
                                   blank=True, null=True, related_name=CREATE_MATERIAL_STOCK)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE,
                                   blank=True, null=True, related_name=UPDATE_MATERIAL_STOCK)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name=MATERIALSTOCKS, null=True)
    is_deleted = models.BooleanField(editable=False, default=False)


