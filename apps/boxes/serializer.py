from django.contrib.auth.models import User
from rest_framework import serializers

from apps.boxes.fields import BoxHyperlinkedIdentityField, BoxHyperlinkedRelatedField
from apps.boxes.models import Box, BoxVersion, BoxProvider


class UserSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="api:user-detail", lookup_field='username')
    boxes = BoxHyperlinkedRelatedField(
        queryset=Box.objects.all(), view_name='api:box-detail', many=True)

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'boxes',)


class BoxProviderSerializer(serializers.ModelSerializer):

    class Meta:
        model = BoxProvider
        fields = ('date_created', 'checksum_type', 'checksum',
                  'description', 'file', )


class BoxVersionSerializer(serializers.ModelSerializer):
    providers = BoxProviderSerializer(many=True, read_only=True)

    class Meta:
        model = BoxVersion
        fields = ('date_created', 'version', 'providers',)


class BoxSerializer(serializers.ModelSerializer):
    url = BoxHyperlinkedIdentityField(view_name="api:box-detail")
    owner = serializers.ReadOnlyField(source='owner.username')
    versions = BoxVersionSerializer(many=True, read_only=True)

    class Meta:
        model = Box
        fields = ('url', 'owner', 'date_created', 'private',
                  'name', 'description', 'versions',)
