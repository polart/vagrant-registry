from django.contrib.auth.models import User
from rest_framework import serializers

from apps.boxes.fields import MultiLookupHyperlinkedIdentityField, MultiLookupHyperlinkedRelatedField
from apps.boxes.models import Box, BoxVersion, BoxProvider, BoxUpload


class UserSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="api:user-detail", lookup_field='username')
    boxes = MultiLookupHyperlinkedRelatedField(
        queryset=Box.objects.all(),
        view_name='api:box-detail',
        many=True,
        multi_lookup_map={'owner.username': 'username', 'name': 'box_name'}
    )

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
    url = MultiLookupHyperlinkedIdentityField(
        view_name="api:box-detail",
        multi_lookup_map={'owner.username': 'username', 'name': 'box_name'}
    )
    owner = serializers.ReadOnlyField(source='owner.username')
    versions = BoxVersionSerializer(many=True, read_only=True)

    class Meta:
        model = Box
        fields = ('url', 'owner', 'date_created', 'private',
                  'name', 'description', 'versions',)


class BoxUploadSerializer(serializers.ModelSerializer):
    url = MultiLookupHyperlinkedIdentityField(
        view_name="api:boxupload-detail",
        multi_lookup_map={
            'box.owner.username': 'username',
            'box.name': 'box_name',
            'pk': 'pk'
        }
    )
    user = serializers.ReadOnlyField(source='box.user.username')
    tag = serializers.ReadOnlyField(source='box.tag')
    status = serializers.SerializerMethodField()
    date_completed = serializers.ReadOnlyField()
    filename = serializers.ReadOnlyField()
    offset = serializers.ReadOnlyField()

    class Meta:
        model = BoxUpload
        fields = ('url', 'id', 'user', 'date_created', 'date_modified',
                  'date_completed', 'filename', 'offset', 'status',
                  'tag', 'checksum_type', 'checksum', 'version',
                  'provider',)

    def get_status(self, obj):
        return obj.get_status_display()
