from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DeleteJob, JobViewSets, RejectOffer, SearchOfferedJobs

router = DefaultRouter()
router.register("api/v1/civil-service-management/job", JobViewSets)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
    path("api/v1/civil-service-management/job/backup/<int:pk>", DeleteJob.as_view()),
    path("api/v1/civil-service-management/job/reject/<int:pk>/", RejectOffer.as_view()),
    path("api/v1/civil-service-management/job/search", SearchOfferedJobs.as_view()),
]
