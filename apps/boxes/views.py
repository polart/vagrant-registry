from django.views.generic import View
from sendfile import sendfile

from apps.boxes.api_views import UserBoxProviderViewSet


class DownloadBoxView(UserBoxProviderViewSet):

    def get(self, request, *args, **kwargs):
        box = self.get_object()
        return sendfile(request, box.file.path)


class BoxMetadataView(View):

    def get(self, request, *args, **kwargs):
        from vagrant_registry.urls import box_metadata_detail
        return box_metadata_detail(request, *args, **kwargs)
