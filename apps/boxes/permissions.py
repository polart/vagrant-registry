from django.http import Http404
from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.boxes.models import BoxMember
from apps.users.models import UserProfile


class BaseBoxPermissions(BasePermission):
    boxes_perms_map = {
        'GET': UserProfile.BOXES_PERM_R,
        'OPTIONS': UserProfile.BOXES_PERM_R,
        'HEAD': UserProfile.BOXES_PERM_R,
        'POST': UserProfile.BOXES_PERM_RW,
        'PUT': UserProfile.BOXES_PERM_RW,
        'PATCH': UserProfile.BOXES_PERM_RW,
        'DELETE': UserProfile.BOXES_PERM_RW,
    }
    obj_perms_map = {
        'GET': BoxMember.PERM_R,
        'OPTIONS': BoxMember.PERM_R,
        'HEAD': BoxMember.PERM_R,
        'POST': BoxMember.PERM_RW,
        'PUT': BoxMember.PERM_RW,
        'PATCH': BoxMember.PERM_RW,
        'DELETE': BoxMember.PERM_RW,
    }

    def has_permission(self, request, view):
        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, '_ignore_model_permissions', False):
            return True

        user = request.user
        if user.is_anonymous():
            return request.method in SAFE_METHODS

        if user.is_staff:
            return True

        return self.boxes_perms_map[request.method] in user.profile.boxes_permissions

    def has_object_permission(self, request, view, obj):
        perms = self.obj_perms_map[request.method]
        if not obj.user_has_perms(request.user, perms):
            # If the user does not have permissions we need to determine if
            # they have read permissions to see 403, or not, and simply see
            # a 404 response.

            if request.method in SAFE_METHODS:
                # Read permissions already checked and failed, no need
                # to make another lookup.
                raise Http404

            read_perms = self.obj_perms_map['GET']
            if not obj.user_has_perms(request.user, read_perms):
                raise Http404

            # Has read permissions.
            return False

        return True


class BoxPermissions(BaseBoxPermissions):
    obj_perms_map = {
        'GET': BoxMember.PERM_R,
        'OPTIONS': BoxMember.PERM_R,
        'HEAD': BoxMember.PERM_R,
        'POST': BoxMember.PERM_OWNER_OR_STAFF,
        'PUT': BoxMember.PERM_OWNER_OR_STAFF,
        'PATCH': BoxMember.PERM_OWNER_OR_STAFF,
        'DELETE': BoxMember.PERM_OWNER_OR_STAFF,
    }


class BoxVersionPermissions(BaseBoxPermissions):
    obj_perms_map = {
        'GET': BoxMember.PERM_R,
        'OPTIONS': BoxMember.PERM_R,
        'HEAD': BoxMember.PERM_R,
        'POST': BoxMember.PERM_RW,
        'PUT': BoxMember.PERM_RW,
        'PATCH': BoxMember.PERM_RW,
        'DELETE': BoxMember.PERM_OWNER_OR_STAFF,
    }


class BoxProviderPermissions(BaseBoxPermissions):
    obj_perms_map = {
        'GET': BoxMember.PERM_R,
        'OPTIONS': BoxMember.PERM_R,
        'HEAD': BoxMember.PERM_R,
        'POST': BoxMember.PERM_RW,
        'PUT': BoxMember.PERM_RW,
        'PATCH': BoxMember.PERM_RW,
        'DELETE': BoxMember.PERM_OWNER_OR_STAFF,
    }


class BoxMemberPermissions(BaseBoxPermissions):
    obj_perms_map = {
        'GET': BoxMember.PERM_OWNER_OR_STAFF,
        'OPTIONS': BoxMember.PERM_R,
        'HEAD': BoxMember.PERM_R,
        'POST': BoxMember.PERM_OWNER_OR_STAFF,
        'PUT': BoxMember.PERM_OWNER_OR_STAFF,
        'PATCH': BoxMember.PERM_OWNER_OR_STAFF,
        'DELETE': BoxMember.PERM_OWNER_OR_STAFF,
    }


class BoxUploadPermissions(BaseBoxPermissions):
    obj_perms_map = {
        'GET': BoxMember.PERM_R,
        'OPTIONS': BoxMember.PERM_R,
        'HEAD': BoxMember.PERM_R,
        'POST': BoxMember.PERM_RW,
        'PUT': BoxMember.PERM_RW,
        'PATCH': BoxMember.PERM_RW,
        'DELETE': BoxMember.PERM_RW,
    }


class IsStaffOrBoxOwnerPermissions(BasePermission):

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated and
            (request.user.is_staff or request.user == obj.owner)
        )


class IsStaffOrRequestedUserPermissions(BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS or
            request.user.is_authenticated and
            (request.user.is_staff or request.user.username == view.kwargs['username'])
        )
