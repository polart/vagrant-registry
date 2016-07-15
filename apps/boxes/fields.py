from collections import OrderedDict

from rest_framework import serializers
from rest_framework.fields import get_attribute
from rest_framework.relations import (
    HyperlinkedIdentityField, HyperlinkedRelatedField)


class MultiLookupHyperlinkedMixin:
    """ Mixin for generating URL for Box instance with multiple lookup fields.

    Multiple lookup fields should be in form of dictionary with fields as keys
    and URL kwarg attributes as values.
    """

    def get_url(self, obj, view_name, request, format):
        """ Given an object, return the URL that hyperlinks to the object.

        May raise a `NoReverseMatch` if the `view_name` is not configured
        to correctly match the URL conf.
        """
        # Unsaved objects will not yet have a valid URL.
        if hasattr(obj, 'pk') and obj.pk in (None, ''):
            return None

        kwargs = {}
        for field, kwarg in self.multi_lookup_map.items():
            kwargs[kwarg] = get_attribute(obj, field.split('.'))

        return self.reverse(
            view_name,
            kwargs=kwargs,
            request=request,
            format=format
        )


class MultiLookupHyperlinkedIdentityField(MultiLookupHyperlinkedMixin,
                                          HyperlinkedIdentityField):
    """
    A read-only field that represents the identity URL for an object, itself.
    """
    def __init__(self, view_name=None, **kwargs):
        self.multi_lookup_map = kwargs.pop(
            'multi_lookup_map', {self.lookup_field, self.lookup_field})
        super().__init__(view_name=view_name, **kwargs)


class MultiLookupHyperlinkedRelatedField(MultiLookupHyperlinkedMixin,
                                         HyperlinkedRelatedField):
    """ A field that represents the URL of relationships to Box object. """
    def __init__(self, view_name=None, **kwargs):
        self.multi_lookup_map = kwargs.pop(
            'multi_lookup_map', {self.lookup_field, self.lookup_field})
        super().__init__(view_name=view_name, **kwargs)


class BoxModelPermissionsField(serializers.Field):
    PERMS_MAP = OrderedDict([
        ('rw', ['boxes.pull_box', 'boxes.push_box']),
        ('r', ['boxes.pull_box']),
        ('', []),
    ])
    PERMS_MAP_REV = {tuple(v): k for k, v in PERMS_MAP.items()}

    def get_attribute(self, user):
        # We pass the object instance onto `to_representation`,
        # not just the field attribute.
        return user

    def get_permissions(self, user):
        return user.get_all_permissions()

    def to_representation(self, user):
        user_perms = self.get_permissions(user)
        for perm_repr, perms in self.PERMS_MAP.items():
            if all([p in user_perms for p in perms]):
                return perm_repr
        return ''

    def to_internal_value(self, data):
        try:
            return self.PERMS_MAP[data]
        except KeyError:
            raise serializers.ValidationError(
                'Invalid permissions. Should be one of {}'
                .format(self.PERMS_MAP.keys())
            )


class BoxObjectPermissionsField(BoxModelPermissionsField):

    def get_permissions(self, user):
        box = getattr(user, '_perm_obj', None)
        return box.get_perms_for_user(user)