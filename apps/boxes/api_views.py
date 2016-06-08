from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404

from apps.boxes.models import Box
from apps.boxes.serializer import UserSerializer, BoxSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'


class BoxViewSet(viewsets.ModelViewSet):
    queryset = Box.objects.all()
    serializer_class = BoxSerializer
    multiple_lookup_fields = ['owner__username', 'name']

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_object(self):
        queryset = self.get_queryset()
        filter = {}
        for field in self.multiple_lookup_fields:
            filter[field] = self.kwargs[field]

        print(filter)

        obj = get_object_or_404(queryset, **filter)
        self.check_object_permissions(self.request, obj)
        return obj
