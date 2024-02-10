from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ShopViewSets, DeleteShop, SearchShop

router = DefaultRouter()
router.register("api/v1/civil-service-management/shop", ShopViewSets)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
    path("api/v1/civil-service-management/shop/backup/<int:pk>", DeleteShop.as_view()),
    path("api/v1/civil-service-management/shop/search", SearchShop.as_view()),
]
