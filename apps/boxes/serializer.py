from itertools import chain

from django.contrib.auth.models import User, Permission
from guardian.shortcuts import remove_perm, assign_perm
from rest_framework import serializers
from rest_framework.serializers import raise_errors_on_nested_writes

from apps.boxes.fields import (
    MultiLookupHyperlinkedIdentityField, MultiLookupHyperlinkedRelatedField)
from apps.boxes.models import Box, BoxVersion, BoxProvider, BoxUpload


class BoxUserPermissionsField(serializers.Field):

    def __init__(self, *args, **kwargs):
        self.perms_map = kwargs.pop('perms_map', {})
        self.perms_map_rev = {v: k for k, v in self.perms_map.items()}
        super().__init__(*args, **kwargs)

    def get_attribute(self, obj):
        # We pass the object instance onto `to_representation`,
        # not just the field attribute.
        return obj

    def to_representation(self, obj):
        return self.perms_map.get(tuple(sorted(obj.get_all_permissions())), '')

    def to_internal_value(self, data):
        if data not in ['r', 'rw', '']:
            raise serializers.ValidationError('invalid perms')
        return self.perms_map_rev.get(data, [])


class UserPermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('name', 'codename', )
        extra_kwargs = {'name': {'read_only': True}}


class UserSerializer(serializers.HyperlinkedModelSerializer):
    PERMS_MAP = {
        ('boxes.pull_box',): 'r',
        ('boxes.pull_box', 'boxes.push_box',): 'rw',
    }
    PERMS_ALL = set(chain(*PERMS_MAP.keys()))

    url = serializers.HyperlinkedIdentityField(
        view_name="api:user-detail", lookup_field='username')
    boxes = MultiLookupHyperlinkedRelatedField(
        view_name='api:box-detail',
        many=True,
        read_only=True,
        multi_lookup_map={'owner.username': 'username', 'name': 'box_name'}
    )
    box_permissions = BoxUserPermissionsField(perms_map=PERMS_MAP)

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'password', 'is_staff',
                  'box_permissions', 'boxes',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data.get('email', ''),
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update_perms(self, instance, validated_data):
        new_perms = validated_data.get('box_permissions', None)
        if new_perms is None:
            return

        for perm in self.PERMS_ALL.difference(new_perms):
            print('remove perm -- ', perm)
            remove_perm(perm, instance)

        for perm in new_perms:
            print('add perm -- ', perm)
            assign_perm(perm, instance)

    def update(self, instance, validated_data):
        print('valid data -- ', validated_data)
        raise_errors_on_nested_writes('update', self, validated_data)

        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()

        self.update_perms(instance, validated_data)
        return instance


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
    url = MultiLookupHyperlinkedIdentityField(
        view_name="api:box-detail",
        multi_lookup_map={
            'owner.username': 'username',
            'name': 'box_name'
        }
    )
    owner = serializers.ReadOnlyField(source='owner.username')
    versions = BoxVersionSerializer(many=True, read_only=True)

    class Meta:
        model = Box
        fields = ('url', 'owner', 'date_created', 'date_modified', 'visibility',
                  'name', 'short_description', 'description', 'versions',)


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
