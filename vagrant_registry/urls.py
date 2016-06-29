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

router = DefaultRouter()
router.register(r'users', api_views.UserViewSet)

box_list = api_views.BoxViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
box_detail = api_views.BoxViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

box_upload_list = api_views.BoxUploadViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
box_upload_detail = api_views.BoxUploadViewSet.as_view({
    'get': 'retrieve',
    'delete': 'destroy'
})

api_urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^boxes/$', box_list, name='box-list'),
    url(r'^boxes/(?P<username>[\w.@+-]+)/(?P<box_name>[\w.@+-]+)/$',
        box_detail, name='box-detail'),
    url(r'^boxes/(?P<username>[\w.@+-]+)/(?P<box_name>[\w.@+-]+)/uploads/$',
        box_upload_list, name='boxupload-list'),
    url(r'^boxes/(?P<username>[\w.@+-]+)/(?P<box_name>[\w.@+-]+)/uploads/(?P<pk>.+)/$',
        api_views.FileUploadView.as_view(), name='boxupload-detail'),
    url(r'^docs/', include('rest_framework_swagger.urls')),
]

urlpatterns = [
    url(r'^api/', include(api_urlpatterns, namespace='api')),
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
