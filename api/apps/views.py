from rest_framework import response
from rest_framework import schemas
from rest_framework.decorators import api_view, renderer_classes
from rest_framework_swagger.renderers import OpenAPIRenderer
from rest_framework_swagger.renderers import SwaggerUIRenderer


@api_view()
@renderer_classes([OpenAPIRenderer, SwaggerUIRenderer])
def schema_view(request):
    from vagrant_registry.urls import api_v1_urlpatterns
    generator = schemas.SchemaGenerator(
        title='Vagrant Registry API v1',
        url='/api/v1/',
        patterns=api_v1_urlpatterns[:-1]    # exclude Docs,
    )
    return response.Response(generator.get_schema(request=request))
