from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import UserPermissions
from apps.users.serializers import UserSerializer, ForStaffUserSerializer


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (UserPermissions,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'

    def get_serializer_class(self):
        if hasattr(self, 'request') and self.request.user.is_staff:
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


class ObtainExpiringAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        if not created:
            # Update the created time of the token to keep it valid
            token.created = timezone.now()
            token.save()
        return Response({'token': token.key})
