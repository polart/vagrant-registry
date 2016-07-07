from collections import namedtuple

import re
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import RetrieveModelMixin, DestroyModelMixin
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.boxes.models import Box, BoxUpload
from apps.boxes.serializer import (
    UserSerializer, BoxSerializer, BoxUploadSerializer, BoxMetadataSerializer)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'


class BoxViewSet(viewsets.ModelViewSet):
    queryset = Box.objects.all()
    serializer_class = BoxSerializer
    multi_lookup_map = {
        'owner__username': 'username',
        'name': 'box_name'
    }

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_object(self):
        queryset = self.get_queryset()
        filters = {}
        for field, kwarg in self.multi_lookup_map.items():
            filters[field] = self.kwargs[kwarg]

        obj = get_object_or_404(queryset, **filters)
        self.check_object_permissions(self.request, obj)
        return obj


class BoxMetadataViewSet(RetrieveModelMixin, GenericViewSet):
    queryset = Box.objects.all()
    serializer_class = BoxMetadataSerializer
    multi_lookup_map = {
        'owner__username': 'username',
        'name': 'box_name'
    }

    def get_object(self):
        queryset = self.get_queryset()
        filters = {}
        for field, kwarg in self.multi_lookup_map.items():
            filters[field] = self.kwargs[kwarg]

        obj = get_object_or_404(queryset, **filters)
        self.check_object_permissions(self.request, obj)
        return obj


class BoxUploadViewSet(viewsets.ModelViewSet):
    queryset = BoxUpload.objects.all()
    serializer_class = BoxUploadSerializer


class BoxUploadParser(FileUploadParser):
    media_type = 'application/octet-stream'

    def get_filename(self, stream, media_type, parser_context):
        return 'vagrant.box'


class FileUploadView(RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = BoxUploadSerializer
    parser_classes = (BoxUploadParser,)
    queryset = BoxUpload.objects.all()
    multi_lookup_map = {
        'box__owner__username': 'username',
        'box__name': 'box_name',
        'pk': 'pk',
    }
    content_range_pattern = re.compile(
        r'^bytes (?P<start>\d+)-(?P<end>\d+)/(?P<total>\d+)$'
    )
    ContentRange = namedtuple('ContentRange', ['start', 'end', 'total'])

    def get_object(self):
        if getattr(self, '_obj', None):
            return self._obj
        queryset = self.get_queryset()
        filters = {}
        for field, kwarg in self.multi_lookup_map.items():
            filters[field] = self.kwargs.pop(kwarg)

        self._obj = get_object_or_404(queryset, **filters)
        self.check_object_permissions(self.request, self._obj)
        return self._obj

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
