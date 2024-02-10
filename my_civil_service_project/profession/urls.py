from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ProfessionViewSets, delete_profession, SearchProfession

router = DefaultRouter()
router.register("api/v1/civil-service-management/worker", ProfessionViewSets)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
    path("api/v1/civil-service-management/worker/backup/<int:pk>", delete_profession),
    path("api/v1/civil-service-management/worker/profession", SearchProfession.as_view()),
]
