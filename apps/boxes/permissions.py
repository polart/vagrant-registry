from django.http import Http404
from rest_framework.permissions import (
    DjangoModelPermissions, SAFE_METHODS)


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
    obj_perms_map = {
        'GET': ['boxes.pull_box'],
        'OPTIONS': ['boxes.pull_box'],
        'HEAD': ['boxes.pull_box'],
        'POST': ['boxes.push_box'],
        'PUT': ['boxes.update_box'],
        'PATCH': ['boxes.update_box'],
        'DELETE': ['boxes.delete_box'],
    }
    authenticated_users_only = False

    def has_permission(self, request, view):
        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, '_ignore_model_permissions', False):
            return True

        user = request.user
        if user.is_anonymous() and request.method in SAFE_METHODS:
            return True

        if user.is_authenticated() and user.is_staff:
            return True

        return (
            user and
            user.is_authenticated() and
            user.has_perms(self.perms_map[request.method])
        )

    def has_object_permission(self, request, view, obj):
        perms = self.obj_perms_map[request.method]
        if not obj.user_has_perms(perms, request.user):
            # If the user does not have permissions we need to determine if
            # they have read permissions to see 403, or not, and simply see
            # a 404 response.

            if request.method in SAFE_METHODS:
                # Read permissions already checked and failed, no need
                # to make another lookup.
                raise Http404

            read_perms = self.obj_perms_map['GET']
            if not obj.user_has_perms(read_perms, request.user):
                raise Http404

            # Has read permissions.
            return False

        return True


