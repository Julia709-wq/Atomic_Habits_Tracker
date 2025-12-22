from django.urls import path
from .views import RegisterApiView
from users.apps import UsersConfig
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView,)

app_name = UsersConfig.name

urlpatterns = [
    path('register/', RegisterApiView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
