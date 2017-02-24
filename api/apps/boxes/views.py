from sendfile import sendfile

from apps.boxes.api_views import UserBoxProviderViewSet


class DownloadBoxView(UserBoxProviderViewSet):

    def get(self, request, *args, **kwargs):
        box = self.get_object()
        box.pulls += 1
        box.save()
        return sendfile(request, box.file.path)
