from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import delete_address, AddressViewSets

router = DefaultRouter()
router.register("api/v1/civil-service-management/address", AddressViewSets)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
    path("api/v1/civil-service-management/address/backup/<int:pk>", delete_address),
]
