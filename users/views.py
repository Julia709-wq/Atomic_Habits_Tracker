from rest_framework import generics, permissions
from .serializers import RegisterSerializer
from users.models import User


class RegisterApiView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny,]

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()
