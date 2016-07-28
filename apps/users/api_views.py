from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import UserPermissions
from apps.users.serializers import UserSerializer, ForStaffUserSerializer


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (UserPermissions,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'

    def get_serializer_class(self):
        if self.request.user.is_staff:
            return ForStaffUserSerializer
        return self.serializer_class


class IsTokenAuthenticated(APIView):
    permission_classes = ()

    def get(self, request, *args, **kwargs):
        token = get_object_or_404(
            Token.objects.all(),
            **{'key': kwargs['token']}
        )
        return Response({'username': token.user.username})
