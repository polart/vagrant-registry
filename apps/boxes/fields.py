from rest_framework.relations import HyperlinkedIdentityField, HyperlinkedRelatedField


class BoxHyperlinkedMixin:
    """ Mixin for generating URL for Box instance with multiple lookup fields. """

    def get_url(self, obj, view_name, request, format):
        """ Given an object, return the URL that hyperlinks to the object.

        May raise a `NoReverseMatch` if the `view_name` is not configured
        to correctly match the URL conf.
        """
        # Unsaved objects will not yet have a valid URL.
        if hasattr(obj, 'pk') and obj.pk in (None, ''):
            return None

        return self.reverse(
            view_name,
            kwargs={
                'owner__username': obj.owner.username,
                'name': obj.name
            },
            request=request,
            format=format
        )


class BoxHyperlinkedIdentityField(BoxHyperlinkedMixin, HyperlinkedIdentityField):
    """
    A read-only field that represents the identity URL for an object, itself.
    """
    pass


class BoxHyperlinkedRelatedField(BoxHyperlinkedMixin, HyperlinkedRelatedField):
    """ A field that represents the URL of relationships to Box object. """
    pass
