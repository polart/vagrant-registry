from rest_framework import serializers

from apps.boxes.fields import (
    MultiLookupHyperlinkedIdentityField)
from apps.boxes.models import (
    Box, BoxVersion, BoxProvider, BoxUpload, BoxMember)


class BoxMemberSerializer(serializers.ModelSerializer):
    url = MultiLookupHyperlinkedIdentityField(
        view_name="api:v1:boxmember-detail",
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
        view_name="api:v1:boxprovider-detail",
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
        fields = ('url', 'tag', 'provider', 'date_created', 'date_modified',
                  'date_updated', 'checksum_type', 'checksum',
                  'download_url', 'file_size', 'pulls', 'status')

    def get_download_url(self, obj):
        if obj.status == BoxProvider.FILLED_IN:
            return self.context.get('request').build_absolute_uri(obj.download_url)
        return None


class BoxVersionSerializer(serializers.ModelSerializer):
    url = MultiLookupHyperlinkedIdentityField(
        view_name="api:v1:boxversion-detail",
        multi_lookup_map={
            'owner.username': 'username',
            'box.name': 'box_name',
            'version': 'version'
        }
    )
    providers = BoxProviderSerializer(many=True, read_only=True)

    class Meta:
        model = BoxVersion
        fields = ('url', 'tag', 'date_created', 'date_modified', 'date_updated',
                  'version', 'changes', 'providers',)


class BoxVersionSimpleSerializer(serializers.ModelSerializer):
    url = MultiLookupHyperlinkedIdentityField(
        view_name="api:v1:boxversion-detail",
        multi_lookup_map={
            'owner.username': 'username',
            'box.name': 'box_name',
            'version': 'version'
        }
    )

    class Meta:
        model = BoxVersion
        fields = ('url', 'tag', 'date_updated', 'version', )


class BoxSerializer(serializers.ModelSerializer):
    PERMS_MAP = {
        ('pull_box',): 'r',
        ('pull_box', 'push_box',): 'rw',
    }

    url = MultiLookupHyperlinkedIdentityField(
        view_name="api:v1:box-detail",
        multi_lookup_map={
            'owner.username': 'username',
            'name': 'box_name'
        }
    )
    owner = serializers.ReadOnlyField(source='owner.username')
    versions = BoxVersionSimpleSerializer(many=True, read_only=True)
    members = serializers.SerializerMethodField()
    user_permissions = serializers.SerializerMethodField()
    pulls = serializers.ReadOnlyField()

    class Meta:
        model = Box
        fields = (
            'url', 'tag', 'owner', 'date_created', 'date_modified', 'date_updated',
            'visibility', 'name', 'short_description', 'description', 'pulls',
            'members', 'user_permissions', 'versions',
        )

    def get_members(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated and (user.is_staff or user == obj.owner):
            return BoxMemberSerializer(
                obj.boxmember_set.all(),
                context={'request': self.context.get('request')},
                many=True,).data
        else:
            return []

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
        view_name="api:v1:boxupload-detail",
        multi_lookup_map={
            'owner.username': 'username',
            'box.name': 'box_name',
            'version.version': 'version',
            'provider.provider': 'provider',
            'checksum': 'checksum',
        }
    )
    user = serializers.ReadOnlyField(source='owner.username')
    tag = serializers.ReadOnlyField(source='box.tag')
    date_completed = serializers.ReadOnlyField()
    date_expires = serializers.ReadOnlyField(source='expires')
    file_size = serializers.IntegerField(required=True)
    offset = serializers.ReadOnlyField()

    class Meta:
        model = BoxUpload
        fields = ('url', 'id', 'user', 'date_created', 'date_modified',
                  'date_completed', 'date_expires', 'file_size', 'offset',
                  'status', 'tag', 'checksum_type', 'checksum', )
        lookup_field = 'checksum'
        extra_kwargs = {
            'url': {'lookup_field': 'checksum'}
        }
