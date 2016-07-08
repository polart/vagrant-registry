from django.shortcuts import get_object_or_404
from django.views.generic import View
from sendfile import sendfile

from apps.boxes.models import BoxProvider


class DownloadBoxView(View):
    queryset = BoxProvider.objects.all()
    multi_lookup_map = {
        'version__box__owner__username': 'username',
        'version__box__name': 'box_name',
        'version__version': 'version',
        'provider': 'provider',
    }

    def get_object(self):
        queryset = self.queryset.all()
        filters = {}
        for field, kwarg in self.multi_lookup_map.items():
            filters[field] = self.kwargs[kwarg]

        obj = get_object_or_404(queryset, **filters)
        # self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request, *args, **kwargs):
        box = self.get_object()
        return sendfile(request, box.file.path)
