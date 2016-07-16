from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import raise_errors_on_nested_writes

from apps.boxes.fields import MultiLookupHyperlinkedRelatedField
from apps.users.models import UserProfile


class UserSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="api:user-detail", lookup_field='username')
    boxes = MultiLookupHyperlinkedRelatedField(
        view_name='api:box-detail',
        many=True,
        read_only=True,
        multi_lookup_map={'owner.username': 'username', 'name': 'box_name'}
    )
    boxes_permissions = serializers.CharField(source='profile.boxes_permissions')

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'password', 'is_staff',
                  'boxes_permissions', 'boxes',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        profile_serializer = UserProfileSerializer(
            data=validated_data['profile'])
        profile_serializer.is_valid(raise_exception=True)

        user = User(
            email=validated_data.get('email', ''),
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()

        profile_serializer.save(user=user)
        return user

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)

        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            elif attr == 'profile':
                profile_serializer = UserProfileSerializer(
                    instance=instance.profile, data=value)
                if profile_serializer.is_valid(raise_exception=True):
                    profile_serializer.save()
            else:
                setattr(instance, attr, value)

        instance.save()
        return instance


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ('boxes_permissions',)
