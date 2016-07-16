from django.contrib.auth.models import User
from guardian.shortcuts import remove_perm, assign_perm
from rest_framework import serializers
from rest_framework.serializers import raise_errors_on_nested_writes

from apps.boxes.fields import MultiLookupHyperlinkedRelatedField, BoxModelPermissionsField
from apps.boxes.models import Box


class UserSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="api:user-detail", lookup_field='username')
    boxes = MultiLookupHyperlinkedRelatedField(
        view_name='api:box-detail',
        many=True,
        read_only=True,
        multi_lookup_map={'owner.username': 'username', 'name': 'box_name'}
    )
    boxes_permissions = BoxModelPermissionsField()

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'password', 'is_staff',
                  'boxes_permissions', 'boxes',)
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
        new_perms = validated_data.get('boxes_permissions', None)
        if new_perms is None:
            return

        for perm in set(Box.all_perms).difference(new_perms):
            remove_perm(perm, instance)

        for perm in new_perms:
            assign_perm(perm, instance)

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)

        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()

        self.update_perms(instance, validated_data)
        return instance