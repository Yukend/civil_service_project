from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSets, DeleteUser, SendOTP, VerifyOTP, login_view

router = DefaultRouter()
router.register("api/v1/civil-service-management/user", UserViewSets)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
    path("token/", login_view),
    path("api/v1/civil-service-management/user/backup/<int:pk>", DeleteUser.as_view()),
    path("api/v1/civil-service-management/email-send-otp/", SendOTP.as_view()),
    path("api/v1/civil-service-management/email-verify-otp/", VerifyOTP.as_view()),
]
