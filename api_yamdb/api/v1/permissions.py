from rest_framework import permissions



class IsSuperUserOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_superuser or
            request.user.is_admin
        )


class AnonimReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
