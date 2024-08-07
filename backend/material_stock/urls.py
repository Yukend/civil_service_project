from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MaterialStockViewSets, SearchMaterial, delete_material_stock

router = DefaultRouter()
router.register("api/v1/civil-service-management/material-stock", MaterialStockViewSets)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
    path(
        "api/v1/civil-service-management/material-stock/backup/<int:pk>",
        delete_material_stock,
    ),
    path(
        "api/v1/civil-service-management/material-stock/search",
        SearchMaterial.as_view(),
    ),
]
