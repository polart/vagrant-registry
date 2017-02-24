from django.http import Http404
from rest_framework.permissions import IsAdminUser, SAFE_METHODS


class UserPermissions(IsAdminUser):

    def has_permission(self, request, view):
        user = request.user
        if user.is_anonymous:
            raise Http404
        return (
            user.is_staff or
            request.method in SAFE_METHODS + ('PATCH',)
        )

    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in SAFE_METHODS or user.is_staff:
            return True
        if request.method in ['PATCH'] and user == obj:
            return True
        return False