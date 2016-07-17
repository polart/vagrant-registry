from rest_framework import serializers

from apps.boxes.fields import (
    MultiLookupHyperlinkedIdentityField)
from apps.boxes.models import (
    Box, BoxVersion, BoxProvider, BoxUpload, BoxMember)


class BoxMemberSerializer(serializers.ModelSerializer):
    url = MultiLookupHyperlinkedIdentityField(
        view_name="api:boxmember-detail",
        multi_lookup_map={
            'box.owner.username': 'username',
            'box.name': 'box_name',
            'user.username': 'member_username',
        }
    )
    username = serializers.SerializerMethodField()

    class Meta:
        model = BoxMember
        fields = ('url', 'username', 'permissions', )

    def get_username(self, obj):
        return obj.user.username


class BoxProviderSerializer(serializers.ModelSerializer):
    url = MultiLookupHyperlinkedIdentityField(
        view_name="api:boxprovider-detail",
        multi_lookup_map={
            'owner.username': 'username',
            'version.box.name': 'box_name',
            'version.version': 'version',
            'provider': 'provider'
        }
    )
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = BoxProvider
        fields = ('url', 'provider', 'date_created', 'date_modified',
                  'checksum_type', 'checksum',
                  'download_url', 'file_size',)

    def get_download_url(self, obj):
        return self.context.get('request').build_absolute_uri(obj.download_url)


class BoxVersionSerializer(serializers.ModelSerializer):
    url = MultiLookupHyperlinkedIdentityField(
        view_name="api:boxversion-detail",
        multi_lookup_map={
            'owner.username': 'username',
            'box.name': 'box_name',
            'version': 'version'
        }
    )
    providers = BoxProviderSerializer(many=True, read_only=True)

    class Meta:
        model = BoxVersion
        fields = ('url', 'date_created', 'date_modified', 'version',
                  'description', 'providers',)


class BoxSerializer(serializers.ModelSerializer):
    PERMS_MAP = {
        ('pull_box',): 'r',
        ('pull_box', 'push_box',): 'rw',
    }

    url = MultiLookupHyperlinkedIdentityField(
        view_name="api:box-detail",
        multi_lookup_map={
            'owner.username': 'username',
            'name': 'box_name'
        }
    )
    owner = serializers.ReadOnlyField(source='owner.username')
    versions = BoxVersionSerializer(many=True, read_only=True)
    members = BoxMemberSerializer(
        many=True, read_only=True, source='boxmember_set')
    user_permissions = serializers.SerializerMethodField()

    class Meta:
        model = Box
        fields = ('url', 'owner', 'date_created', 'date_modified', 'visibility',
                  'name', 'short_description', 'description', 'members',
                  'user_permissions', 'versions',)

    def get_user_permissions(self, obj):
        user = self.context.get('request').user
        return obj.get_perms_for_user(user)


class BoxProviderMetadataSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='provider')
    url = serializers.SerializerMethodField('get_download_url')

    class Meta:
        model = BoxProvider
        fields = ('name', 'url', 'checksum_type', 'checksum',)

    def get_download_url(self, obj):
        return self.context.get('request').build_absolute_uri(obj.download_url)


class BoxVersionMetadataSerializer(serializers.ModelSerializer):
    providers = BoxProviderMetadataSerializer(many=True, read_only=True)

    class Meta:
        model = BoxVersion
        fields = ('version', 'providers',)


class BoxMetadataSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='tag', read_only=True)
    description = serializers.CharField(
        source='short_description', read_only=True)
    versions = BoxVersionMetadataSerializer(many=True, read_only=True)

    class Meta:
        model = Box
        fields = ('name', 'description', 'versions',)


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
    file_size = serializers.IntegerField(required=True)
    offset = serializers.ReadOnlyField()

    class Meta:
        model = BoxUpload
        fields = ('url', 'id', 'user', 'date_created', 'date_modified',
                  'date_completed', 'file_size', 'offset', 'status',
                  'tag', 'checksum_type', 'checksum', 'version',
                  'provider',)

    def get_status(self, obj):
        return obj.get_status_display()
