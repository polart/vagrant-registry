from sendfile import sendfile

from apps.boxes.api_views import BoxProviderViewSet


class DownloadBoxView(BoxProviderViewSet):

    def get(self, request, *args, **kwargs):
        provider = self.get_object()
        provider.pulls += 1
        # Date modified should not be updated
        provider.save(update_fields=['pulls'])
        return sendfile(request, provider.file.path)
