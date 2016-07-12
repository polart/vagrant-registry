from rest_framework.permissions import (
    DjangoModelPermissions, IsAdminUser, SAFE_METHODS)

from apps.boxes.models import Box


class BoxPermissions(DjangoModelPermissions):
    perms_map = {
        'GET': ['boxes.pull_box'],
        'OPTIONS': ['boxes.pull_box'],
        'HEAD': ['boxes.pull_box'],
        'POST': ['boxes.push_box'],
        'PUT': ['boxes.push_box'],
        'PATCH': ['boxes.push_box'],
        'DELETE': ['boxes.push_box'],
    }
    authenticated_users_only = False

    def has_object_permission(self, request, view, obj):
        is_authenticated = request.user and request.user.is_authenticated()
        is_staff = is_authenticated and request.user.is_staff
        is_owner = is_authenticated and obj.owner == request.user

        if is_staff or is_owner:
            # Staff and owner have all permissions on the box
            return True

        if request.method in SAFE_METHODS:
            if obj.visibility == Box.PUBLIC:
                return True
            elif obj.visibility == Box.USERS:
                return is_authenticated
            elif obj.visibility == Box.PRIVATE:
                return (
                    is_authenticated and
                    request.user.has_perm(self.perms_map[request.method], obj)
                )
            else:
                # Unrecognised visibility option
                return False

        else:
            return (
                is_authenticated and
                request.user.has_perm(self.perms_map[request.method], obj)
            )


class IsStaffUserOrReadOnly(IsAdminUser):

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_staff
        )
