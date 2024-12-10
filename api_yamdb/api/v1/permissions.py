from rest_framework import permissions


class IsSuperUserOrIsAdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_superuser or request.user.is_admin
        )


class AnonimReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsAuthorModeratorAdminSuperUserOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user == obj.author
            or request.user.is_moderator
            or request.user.is_admin
        )


class IsAdminUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.is_admin if request.user.is_authenticated else False
        )
