from django.contrib.auth.models import User
from rest_framework import viewsets

from apps.users.permissions import UserPermissions
from apps.users.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (UserPermissions,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
