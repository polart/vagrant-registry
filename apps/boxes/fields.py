from rest_framework.fields import get_attribute
from rest_framework.relations import HyperlinkedIdentityField, HyperlinkedRelatedField


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
