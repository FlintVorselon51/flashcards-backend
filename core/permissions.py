# core/permissions.py
from rest_framework import permissions


class IsOwnerOrReadOnlyIfPublic(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            if hasattr(obj, 'is_public'):
                return obj.owner == request.user or obj.is_public
            elif hasattr(obj, 'deck'):
                return obj.deck.owner == request.user or obj.deck.is_public

        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'deck'):
            return obj.deck.owner == request.user

        return False
