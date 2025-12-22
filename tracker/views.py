from rest_framework import viewsets, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Habit
from .serializers import HabitSerializer
from .permissions import IsOwnerOrReadOnly
from .paginators import HabitsPaginator


class HabitViewSet(viewsets.ModelViewSet):
    """ViewSet для CRUD привычек"""

    serializer_class = HabitSerializer
    pagination_class = HabitsPaginator
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user and user.is_authenticated:
            return Habit.objects.filter(owner=user)
        return Habit.objects.none()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def public(self, request):
        """Получить список всех публичных привычек"""
        public_habits = Habit.objects.filter(is_public=True)
        serializer = self.get_serializer(public_habits, many=True)
        return Response(serializer.data)
