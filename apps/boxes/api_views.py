from collections import namedtuple

import re
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.http import Http404
from rest_framework import status
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import (
    RetrieveModelMixin, DestroyModelMixin, ListModelMixin)
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.boxes.models import Box, BoxUpload, BoxVersion, BoxProvider
from apps.boxes.permissions import (
    BoxPermissions, BaseBoxPermissions, BoxMemberPermissions,
    BoxProviderPermissions, BoxVersionPermissions,
    IsStaffOrRequestedUserPermissions, BoxUploadPermissions)
from apps.boxes.serializers import (
    BoxSerializer, BoxUploadSerializer, BoxMetadataSerializer,
    BoxVersionSerializer, BoxProviderSerializer, BoxMemberSerializer)


class UserBoxMixin:
    box_permission_classes = (BaseBoxPermissions, )

    def get_box_object_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        return [permission() for permission in self.box_permission_classes]

    def check_box_object_permissions(self, request, obj):
        """
        Check if the request should be permitted for a given object.
        Raises an appropriate exception if the request is not permitted.
        """
        for permission in self.get_box_object_permissions():
            if not permission.has_object_permission(request, self, obj):
                self.permission_denied(
                    request, message=getattr(permission, 'message', None)
                )

    def get_user_object(self):
        try:
            return User.objects.get(username=self.kwargs['username'])
        except User.DoesNotExist:
            raise Http404

    def get_box_object(self):
        # No need to filter queryset, because filtering is done
        # in `get_box_queryset`
        queryset = self.get_box_queryset()

        obj = get_object_or_404(queryset, **{
            'name': self.kwargs['box_name']
        })

        # May raise a permission denied
        self.check_box_object_permissions(self.request, obj)

        return obj

    def get_box_queryset(self):
        return (Box.objects
                .by_owner(self.get_user_object())
                .for_user(self.request.user))


class BoxViewSet(ListModelMixin, GenericViewSet):
    permission_classes = (BoxPermissions, )
    queryset = Box.objects.all()
    serializer_class = BoxSerializer

    def get_queryset(self):
        return Box.objects.for_user(self.request.user)


class UserBoxViewSet(UserBoxMixin, viewsets.ModelViewSet):
    permission_classes = (IsStaffOrRequestedUserPermissions, BoxPermissions, )
    queryset = Box.objects.all()
    serializer_class = BoxSerializer

    def get_queryset(self):
        return self.get_box_queryset()

    def get_object(self):
        return self.get_box_object()

    def perform_create(self, serializer):
        user = self.get_user_object()
        try:
            serializer.save(owner=user)
        except IntegrityError:
            raise ValidationError("User {} already has box with the name '{}'"
                                  .format(user, serializer.initial_data['name']))


class UserBoxMemberViewSet(UserBoxMixin, viewsets.ModelViewSet):
    permission_classes = (IsStaffOrRequestedUserPermissions, BoxMemberPermissions, )
    queryset = Box.objects.all()
    serializer_class = BoxMemberSerializer
    lookup_field = 'user__username'
    lookup_url_kwarg = 'member_username'

    def get_queryset(self):
        box = self.get_box_object()
        if self.request.user.is_staff or self.request.user == box.owner:
            return box.boxmember_set.all()
        return box.boxmember_set.none()

    def perform_create(self, serializer):
        try:
            user = User.objects.get(username=self.kwargs['member_username'])
        except User.DoesNotExist:
            raise Http404
        try:
            serializer.save(box=self.get_box_object(), user=user)
        except IntegrityError:
            raise ValidationError("User '{}' already added to the box"
                                  .format(user))


class UserBoxVersionViewSet(UserBoxMixin, viewsets.ModelViewSet):
    permission_classes = (BoxVersionPermissions, )
    queryset = BoxVersion.objects.none()
    serializer_class = BoxVersionSerializer
    lookup_field = 'version'
    lookup_url_kwarg = 'version'

    def get_queryset(self):
        return self.get_box_object().versions.all()

    def perform_create(self, serializer):
        serializer.save(box=self.get_box_object())


class UserBoxProviderViewSet(UserBoxMixin, viewsets.ModelViewSet):
    permission_classes = (BoxProviderPermissions, )
    queryset = BoxProvider.objects.none()
    serializer_class = BoxProviderSerializer
    lookup_field = 'provider'
    lookup_url_kwarg = 'provider'

    def get_box_version_object(self):
        return get_object_or_404(
            self.get_box_object().versions.all(),
            **{'version': self.kwargs['version']}
        )

    def get_queryset(self):
        return self.get_box_version_object().providers.all()


class UserBoxMetadataViewSet(UserBoxViewSet):
    serializer_class = BoxMetadataSerializer


class UserBoxUploadViewSet(UserBoxMixin, viewsets.ModelViewSet):
    permission_classes = (BoxUploadPermissions, )
    queryset = BoxUpload.objects.all()
    serializer_class = BoxUploadSerializer

    def get_queryset(self):
        return self.get_box_object().uploads.all()

    def perform_create(self, serializer):
        box = self.get_box_object()
        version = serializer.validated_data['version']
        provider = serializer.validated_data['provider']
        try:
            (box
             .versions.get(version=version)
             .providers.get(provider=provider))
            raise ValidationError(
                'Provider "{}" already exists for version "{}"'
                .format(provider, version)
            )
        except (BoxVersion.DoesNotExist, BoxProvider.DoesNotExist):
            serializer.save(box=box)


class BoxUploadParser(FileUploadParser):
    media_type = 'application/octet-stream'

    def get_filename(self, stream, media_type, parser_context):
        return 'vagrant.box'


class UserBoxUploadHandlerViewSet(UserBoxMixin, RetrieveModelMixin,
                                  DestroyModelMixin, GenericViewSet):
    permission_classes = (BoxUploadPermissions, )
    serializer_class = BoxUploadSerializer
    parser_classes = (BoxUploadParser,)
    queryset = BoxUpload.objects.none()

    content_range_pattern = re.compile(
        r'^bytes (?P<start>\d+)-(?P<end>\d+)/(?P<total>\d+)$'
    )
    ContentRange = namedtuple('ContentRange', ['start', 'end', 'total'])

    def _get_content_range_header(self, request):
        content_range = request.META.get('HTTP_CONTENT_RANGE', '')
        match = self.content_range_pattern.match(content_range)
        if match:
            return self.ContentRange(
                start=int(match.group('start')),
                end=int(match.group('end')),
                total=int(match.group('total')),
            )
        else:
            return None

    def _get_range_not_satisfiable_response(self, msg):
        box_upload = self.get_object()
        return Response(
            status=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
            data={'detail': msg,
                  'offset': box_upload.offset,
                  'file_size': box_upload.file_size})

    def get_queryset(self):
        return self.get_box_object().uploads.all()

    def update(self, request, **kwargs):
        box_upload = self.get_object()

        new_chunk = request.data.get('file')
        if not new_chunk:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'detail': "File data wasn't provided."})

        crange = self._get_content_range_header(request)
        if not crange:
            return self._get_range_not_satisfiable_response(
                '"Content-Range" header is missing or invalid.')
        if box_upload.offset != crange.start:
            return self._get_range_not_satisfiable_response(
                "First byte position ({}) doesn't much current offset ({})."
                .format(crange.start, box_upload.offset))
        if box_upload.file_size != crange.total:
            return self._get_range_not_satisfiable_response(
                "Complete length ({}) specified in header doesn't match "
                "file size ({}) specified when upload was initiated."
                .format(crange.total, box_upload.file_size))
        if crange.end > crange.total:
            return self._get_range_not_satisfiable_response(
                'Last byte position ({}) is greater than complete '
                'length ({}).'
                .format(crange.end, crange.total))
        if new_chunk.size != crange.end - crange.start:
            return self._get_range_not_satisfiable_response(
                "Uploaded content length ({}) doesn't much content "
                "range ({}) specified in the header."
                .format(new_chunk.size, crange.end - crange.start))

        try:
            box_upload.append_chunk(new_chunk)
        except AssertionError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'detail': str(e)})

        serializer = self.get_serializer(box_upload)
        if crange.end == crange.total:
            return Response(data=serializer.data,
                            status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.data,
                            status=status.HTTP_202_ACCEPTED)
