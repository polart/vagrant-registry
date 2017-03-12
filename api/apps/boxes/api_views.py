import logging
from collections import namedtuple

import re

from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.http import Http404
from rest_framework import status
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError, ParseError, APIException
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import (
    RetrieveModelMixin, DestroyModelMixin, ListModelMixin)
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.api_exceptions import CustomApiException
from apps.boxes.models import Box, BoxUpload, BoxVersion, BoxProvider
from apps.boxes.permissions import (
    BoxPermissions, BaseBoxPermissions, BoxMemberPermissions,
    BoxProviderPermissions, BoxVersionPermissions,
    IsStaffOrRequestedUserPermissions, BoxUploadPermissions)
from apps.boxes.serializers import (
    BoxSerializer, BoxUploadSerializer, BoxMetadataSerializer,
    BoxVersionSerializer, BoxProviderSerializer, BoxMemberSerializer)


logger = logging.getLogger(__name__)

User = get_user_model()


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

    def get_box_version_object(self):
        return get_object_or_404(
            self.get_box_object().versions.all(),
            **{'version': self.kwargs['version']}
        )

    def get_box_provider_object(self):
        return get_object_or_404(
            self.get_box_version_object().providers.all(),
            **{'provider': self.kwargs['provider']}
        )

    def get_box_queryset(self):
        return (
            Box.objects
            .by_owner(self.get_user_object())
            .for_user(self.request.user)
            .select_related('owner')
        )


class BoxViewSet(ListModelMixin, GenericViewSet):
    permission_classes = (BoxPermissions, )
    queryset = Box.objects.all()
    serializer_class = BoxSerializer
    ordering_fields = ('pulls', 'date_updated')
    search_fields = ('name', 'short_description',
                     '=versions__providers__provider', )

    def get_queryset(self):
        return Box.objects.for_user(self.request.user)\
            .annotate_pulls().order_by('-pulls')


class UserBoxViewSet(UserBoxMixin, viewsets.ModelViewSet):
    permission_classes = (IsStaffOrRequestedUserPermissions, BoxPermissions, )
    queryset = Box.objects.all()
    serializer_class = BoxSerializer
    ordering_fields = ('pulls', 'date_updated')
    search_fields = ('name', 'short_description',
                     '=versions__providers__provider', )

    def get_box_queryset(self):
        # Annotating in `get_box_queryset`, so 'detail' API
        # for a single object will also be annotated
        return super(UserBoxViewSet, self).get_box_queryset()\
            .annotate_pulls().order_by('-pulls')

    def get_queryset(self):
        return self.get_box_queryset()

    def get_object(self):
        return self.get_box_object()

    def perform_create(self, serializer):
        user = self.get_user_object()
        try:
            box = serializer.save(owner=user)
            logger.info('New box created: {}'.format(box))
        except IntegrityError:
            raise ValidationError("User {} already has box with the name '{}'"
                                  .format(user, serializer.initial_data['name']))


class BoxMemberViewSet(UserBoxMixin, viewsets.ModelViewSet):
    permission_classes = (IsStaffOrRequestedUserPermissions, BoxMemberPermissions, )
    queryset = Box.objects.all()
    serializer_class = BoxMemberSerializer
    lookup_field = 'user__username'
    lookup_url_kwarg = 'member_username'
    ordering_fields = ('user__username', )
    search_fields = ('user__username', )

    def get_queryset(self):
        box = self.get_box_object()
        if self.request.user.is_staff or self.request.user == box.owner:
            return box.boxmember_set.all().order_by('user__username')
        return box.boxmember_set.none()

    def perform_create(self, serializer):
        try:
            user = User.objects.get(username=self.kwargs['member_username'])
        except User.DoesNotExist:
            raise Http404

        box = self.get_box_object()
        try:
            serializer.save(box=box, user=user)
            logger.info('Box {} shared with user {}'.format(box, user))
        except IntegrityError:
            raise ValidationError("User '{}' already added to the box"
                                  .format(user))


class BoxVersionViewSet(UserBoxMixin, viewsets.ModelViewSet):
    permission_classes = (BoxVersionPermissions, )
    queryset = BoxVersion.objects.none()
    serializer_class = BoxVersionSerializer
    lookup_field = 'version'
    lookup_url_kwarg = 'version'
    ordering_fields = ('date_updated', )
    search_fields = ('version', '=providers__provider', )

    def get_queryset(self):
        return self.get_box_object().versions.all().order_by('-date_updated')

    def perform_create(self, serializer):
        box = self.get_box_object()
        version = serializer.save(box=box)
        logger.info('New version created: {}'.format(version))


class BoxProviderViewSet(UserBoxMixin, viewsets.ModelViewSet):
    permission_classes = (BoxProviderPermissions, )
    queryset = BoxProvider.objects.none()
    serializer_class = BoxProviderSerializer
    lookup_field = 'provider'
    lookup_url_kwarg = 'provider'
    ordering_fields = ('pulls', 'date_updated', )
    search_fields = ('=provider', )

    def get_queryset(self):
        return self.get_box_version_object().providers.all()\
            .order_by('-date_updated')

    def perform_create(self, serializer):
        version = self.get_box_version_object()
        provider = serializer.save(version=version)
        logger.info('New provider created: {}'.format(provider))


class BoxMetadataViewSet(UserBoxViewSet):
    serializer_class = BoxMetadataSerializer


class BoxUploadViewSet(UserBoxMixin, viewsets.ModelViewSet):
    permission_classes = (BoxUploadPermissions, )
    queryset = BoxUpload.objects.all()
    serializer_class = BoxUploadSerializer
    ordering_fields = ('date_modified', )
    search_fields = ()

    def get_queryset(self):
        return self.get_box_provider_object().uploads.all()\
            .order_by('-date_modified')

    def perform_create(self, serializer):
        provider = self.get_box_provider_object()

        if provider.status == BoxProvider.FILLED_IN:
            raise CustomApiException(
                detail="Provider already has box file.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        upload = serializer.save(provider=provider)
        logger.info('New upload initiated: {}'.format(upload))


class BoxUploadParser(FileUploadParser):
    media_type = 'application/octet-stream'

    def get_filename(self, stream, media_type, parser_context):
        return 'vagrant.box'


class BoxUploadHandlerViewSet(UserBoxMixin, RetrieveModelMixin,
                              DestroyModelMixin, GenericViewSet):
    permission_classes = (BoxUploadPermissions, )
    serializer_class = BoxUploadSerializer
    parser_classes = (BoxUploadParser,)
    queryset = BoxUpload.objects.none()
    ordering_fields = ('date_modified', )

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
        return self.get_box_provider_object().uploads.all()

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
        # Range is zero-indexed
        if crange.end >= crange.total:
            return self._get_range_not_satisfiable_response(
                'Last byte position ({}) is greater than complete '
                'length ({}).'
                .format(crange.end, crange.total))
        # Range is zero-indexed
        if new_chunk.size != crange.end - crange.start + 1:
            return self._get_range_not_satisfiable_response(
                "Uploaded content length ({}) doesn't much content "
                "range ({}) specified in the header."
                .format(new_chunk.size, crange.end - crange.start + 1))

        try:
            box_upload.append_chunk(new_chunk)
        except AssertionError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'detail': str(e)})

        serializer = self.get_serializer(box_upload)
        # Range is zero-indexed
        if crange.end == crange.total - 1:
            return Response(data=serializer.data,
                            status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.data,
                            status=status.HTTP_202_ACCEPTED)
