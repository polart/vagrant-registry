from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework.routers import DefaultRouter

from apps.users import api_views as users_api_views
from apps.boxes import api_views as boxes_api_views
from apps.boxes.views import DownloadBoxView
from apps.views import schema_view

admin.site.site_header = 'Vagrant Registry Administration'
admin.site.site_title = 'Vagrant Registry Administration'


router = DefaultRouter()
router.register(r'users', users_api_views.UserViewSet)

all_box_list = boxes_api_views.BoxViewSet.as_view({
    'get': 'list',
})

box_list = boxes_api_views.UserBoxViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
box_detail = boxes_api_views.UserBoxViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

box_member_list = boxes_api_views.UserBoxMemberViewSet.as_view({
    'get': 'list',
})
box_member_detail = boxes_api_views.UserBoxMemberViewSet.as_view({
    'get': 'retrieve',
    'post': 'create',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

box_version_list = boxes_api_views.UserBoxVersionViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
box_version_detail = boxes_api_views.UserBoxVersionViewSet.as_view({
    'get': 'retrieve',
    'delete': 'destroy'
})

box_provider_list = boxes_api_views.UserBoxProviderViewSet.as_view({
    'get': 'list',
})
box_provider_detail = boxes_api_views.UserBoxProviderViewSet.as_view({
    'get': 'retrieve',
    'delete': 'destroy'
})

box_upload_list = boxes_api_views.UserBoxUploadViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
box_upload_detail = boxes_api_views.UserBoxUploadHandlerViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})
box_metadata_detail = boxes_api_views.UserBoxMetadataViewSet.as_view({
    'get': 'retrieve',
})

api_v1_urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^boxes/$', all_box_list, name='boxall-list'),
    url(r'^boxes/(?P<username>[\w.@+-]+)/$', box_list, name='box-list'),
    url(r'^boxes/(?P<username>[\w.@+-]+)/(?P<box_name>[\w.@+-]+)/$',
        box_detail, name='box-detail'),
    url(r'^boxes/(?P<username>[\w.@+-]+)/(?P<box_name>[\w.@+-]+)/members/$',
        box_member_list, name='boxmember-list'),
    url(r'^boxes/(?P<username>[\w.@+-]+)/(?P<box_name>[\w.@+-]+)/members/'
        r'(?P<member_username>[\w.@+-]+)/$',
        box_member_detail, name='boxmember-detail'),
    url(r'^boxes/(?P<username>[\w.@+-]+)/(?P<box_name>[\w.@+-]+)/metadata/$',
        box_metadata_detail, name='boxmetadata-detail'),
    url(r'^boxes/(?P<username>[\w.@+-]+)/(?P<box_name>[\w.@+-]+)/versions/$',
        box_version_list, name='boxversion-list'),
    url(r'^boxes/(?P<username>[\w.@+-]+)/(?P<box_name>[\w.@+-]+)/versions/'
        r'(?P<version>\d+\.\d+\.\d+)/$',
        box_version_detail, name='boxversion-detail'),
    url(r'^boxes/(?P<username>[\w.@+-]+)/(?P<box_name>[\w.@+-]+)/versions/'
        r'(?P<version>\d+\.\d+\.\d+)/providers/$',
        box_provider_list, name='boxprovider-list'),
    url(r'^boxes/(?P<username>[\w.@+-]+)/(?P<box_name>[\w.@+-]+)/versions/'
        r'(?P<version>\d+\.\d+\.\d+)/providers/(?P<provider>[\w.@+-]+)/$',
        box_provider_detail, name='boxprovider-detail'),
    url(r'^boxes/(?P<username>[\w.@+-]+)/(?P<box_name>[\w.@+-]+)/uploads/$',
        box_upload_list, name='boxupload-list'),
    url(r'^boxes/(?P<username>[\w.@+-]+)/(?P<box_name>[\w.@+-]+)/uploads/(?P<pk>.+)/$',
        box_upload_detail, name='boxupload-detail'),
    url(r'^auth/', include('rest_framework.urls')),
    url(r'^tokens/$', users_api_views.ObtainExpiringAuthToken.as_view()),
    url(r'^tokens/(?P<token>\w+)/',
        users_api_views.IsTokenAuthenticated.as_view()),
    url(r'^docs/', schema_view, name='schema-view'),
]

api_urlpatterns = [
    url(r'^v1/', include(api_v1_urlpatterns, namespace='v1')),
    # Latest API without explicit version
    url(r'^', include(api_v1_urlpatterns, namespace='v1')),
]

urlpatterns = [
    url(r'^api/', include(api_urlpatterns, namespace='api')),
    url(r'^admin/', admin.site.urls),
    url(r'^downloads/boxes/(?P<username>[\w.@+-]+)/(?P<box_name>[\w.@+-]+)/'
        r'(?P<version>\d+\.\d+\.\d+)/'
        r'(?P<provider>[\w.@+-]+).box',
        DownloadBoxView.as_view({'get': 'get'}), name='downloads-box'),
    url(r'^box-metadata/(?P<username>[\w.@+-]+)/(?P<box_name>[\w.@+-]+)/$',
        box_metadata_detail, name='box-metadata'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)