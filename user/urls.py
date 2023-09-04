from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views


app_name = 'user'

router = DefaultRouter()
router.register('auth', views.AuthUserView, basename='auth')

urlpatterns = []
urlpatterns += router.urls
