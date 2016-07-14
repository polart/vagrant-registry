"""vagrant_registry URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework.routers import DefaultRouter

from apps.boxes import api_views
from apps.boxes.views import DownloadBoxView, BoxMetadataView

router = DefaultRouter()
router.register(r'users', api_views.UserViewSet)

all_box_list = api_views.AllBoxViewSet.as_view({
    'get': 'list',
})

box_list = api_views.UserBoxViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
box_detail = api_views.UserBoxViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

team_box_list = api_views.TeamBoxViewSet.as_view({
    'get': 'list',
})
team_box_detail = api_views.TeamBoxViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})

box_version_list = api_views.BoxVersionViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
box_version_detail = api_views.BoxVersionViewSet.as_view({
    'get': 'retrieve',
    # 'put': 'update',
    # 'patch': 'partial_update',
    'delete': 'destroy'
})

box_provider_list = api_views.BoxProviderViewSet.as_view({
    'get': 'list',
    # 'post': 'create'
})
box_provider_detail = api_views.BoxProviderViewSet.as_view({
    'get': 'retrieve',
    # 'put': 'update',
    # 'patch': 'partial_update',
    'delete': 'destroy'
})

box_upload_list = api_views.BoxUploadViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
box_upload_detail = api_views.FileUploadView.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})
box_metadata_detail = api_views.BoxMetadataViewSet.as_view({
    'get': 'retrieve',
})

api_urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^boxes/$', all_box_list, name='boxall-list'),
    url(r'^boxes/(?P<username>[\w.@+-]+)/$', box_list, name='box-list'),
    url(r'^boxes/(?P<username>[\w.@+-]+)/(?P<box_name>[\w.@+-]+)/$',
        box_detail, name='box-detail'),
    url(r'^boxes/(?P<username>[\w.@+-]+)/(?P<box_name>[\w.@+-]+)/team/$',
        team_box_list, name='teambox-list'),
    url(r'^boxes/(?P<username>[\w.@+-]+)/(?P<box_name>[\w.@+-]+)/team/'
        r'(?P<member_username>[\w.@+-]+)/$',
        team_box_detail, name='teambox-detail'),
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
    url(r'^docs/', include('rest_framework_swagger.urls')),
]

urlpatterns = [
    url(r'^api/', include(api_urlpatterns, namespace='api')),
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls')),

    url(r'^downloads/boxes/(?P<username>[\w.@+-]+)/(?P<box_name>[\w.@+-]+)/'
        r'version/(?P<version>\d+\.\d+\.\d+)/'
        r'provider/(?P<provider>[\w.@+-]+)/$',
        DownloadBoxView.as_view(), name='downloads-box'),
    url(r'^(?P<username>[\w.@+-]+)/(?P<box_name>[\w.@+-]+)/$',
        BoxMetadataView.as_view(), name='box-metadata'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
