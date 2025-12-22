from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Доступно для чтения всем, изменение только владельцу"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class IsOwnerOnly(permissions.BasePermission):
    """Доступ владельца к CRUD"""

    def has_object_permission(self, request, view, obj):
        return obj == request.user
