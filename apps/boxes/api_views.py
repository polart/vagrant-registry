from collections import namedtuple

import re
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import RetrieveModelMixin, DestroyModelMixin, ListModelMixin
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.boxes.models import Box, BoxUpload, BoxVersion, BoxProvider
from apps.boxes.permissions import BoxPermissions, IsStaffUserOrReadOnly
from apps.boxes.serializer import (
    UserSerializer, BoxSerializer, BoxUploadSerializer, BoxMetadataSerializer, BoxVersionSerializer,
    BoxProviderSerializer)


class QuerySetFilterMixin:
    # model_field : url_kwarg
    queryset_filters = {}

    def get_queryset(self):
        queryset = super().get_queryset()
        filters = {}
        for model_field, url_kwarg in self.queryset_filters.items():
            filters[model_field] = self.kwargs[url_kwarg]
        return queryset.filter(**filters)


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsStaffUserOrReadOnly, )
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'


class AllBoxViewSet(ListModelMixin, GenericViewSet):
    queryset = Box.objects.all()
    serializer_class = BoxSerializer


class UserBoxViewSet(QuerySetFilterMixin, viewsets.ModelViewSet):
    permission_classes = (BoxPermissions, )
    queryset = Box.objects.all()
    serializer_class = BoxSerializer
    lookup_field = 'name'
    lookup_url_kwarg = 'box_name'
    queryset_filters = {'owner__username': 'username'}

    def perform_create(self, serializer):
        owner = get_object_or_404(
            User.objects.all(),
            **{
                'username': self.kwargs['username'],
            }
        )
        serializer.save(owner=owner)


class BoxVersionViewSet(QuerySetFilterMixin, viewsets.ModelViewSet):
    permission_classes = (BoxPermissions, )
    queryset = BoxVersion.objects.all()
    serializer_class = BoxVersionSerializer
    lookup_field = 'version'
    lookup_url_kwarg = 'version'
    queryset_filters = {
        'box__owner__username': 'username',
        'box__name': 'box_name'
    }

    def perform_create(self, serializer):
        box = get_object_or_404(
            Box.objects.all(),
            **{
                'box__owner__username': self.kwargs['username'],
                'box__name': self.kwargs['box_name'],
            }
        )
        serializer.save(box=box)


class BoxProviderViewSet(QuerySetFilterMixin, viewsets.ModelViewSet):
    permission_classes = (BoxPermissions, )
    queryset = BoxProvider.objects.all()
    serializer_class = BoxProviderSerializer
    lookup_field = 'provider'
    lookup_url_kwarg = 'provider'
    queryset_filters = {
        'version__box__owner__username': 'username',
        'version__box__name': 'box_name',
        'version__version': 'version',
    }

    def perform_create(self, serializer):
        box_version = get_object_or_404(
            BoxVersion.objects.all(),
            **{
                'version__box__owner__username': self.kwargs['username'],
                'version__box__name': self.kwargs['box_name'],
                'version__version': self.kwargs['version'],
            }
        )
        serializer.save(version=box_version)


class BoxMetadataViewSet(QuerySetFilterMixin, RetrieveModelMixin,
                         GenericViewSet):
    permission_classes = (BoxPermissions, )
    queryset = Box.objects.all()
    serializer_class = BoxMetadataSerializer
    lookup_field = 'name'
    lookup_url_kwarg = 'box_name'
    queryset_filters = {'owner__username': 'username'}


class BoxUploadViewSet(QuerySetFilterMixin, viewsets.ModelViewSet):
    permission_classes = (BoxPermissions, )
    queryset = BoxUpload.objects.all()
    serializer_class = BoxUploadSerializer
    queryset_filters = {
        'box__owner__username': 'username',
        'box__name': 'box_name'
    }

    def perform_create(self, serializer):
        box = get_object_or_404(
            Box.objects.all(),
            **{
                'owner__username': self.kwargs['username'],
                'name': self.kwargs['box_name'],
            }
        )
        serializer.save(box=box)


class BoxUploadParser(FileUploadParser):
    media_type = 'application/octet-stream'

    def get_filename(self, stream, media_type, parser_context):
        return 'vagrant.box'


class FileUploadView(QuerySetFilterMixin, RetrieveModelMixin,
                     DestroyModelMixin, GenericViewSet):
    permission_classes = (BoxPermissions, )
    serializer_class = BoxUploadSerializer
    parser_classes = (BoxUploadParser,)
    queryset = BoxUpload.objects.all()
    queryset_filters = {
        'box__owner__username': 'username',
        'box__name': 'box_name'
    }

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
