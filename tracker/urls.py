from tracker.apps import TrackerConfig
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import HabitViewSet


app_name = TrackerConfig.name

router = DefaultRouter()
router.register(r'habits', HabitViewSet, basename='habits')

urlpatterns = [
    path('', include(router.urls)),
]
