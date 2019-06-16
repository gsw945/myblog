"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path, reverse
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.templatetags.staticfiles import static as static_url
from django.views.generic.base import RedirectView

from .views import markdown_uploader

admin.site.site_header = '玖亖伍•管理'
admin.site.index_title = '后台主页'
admin.site.site_title = '管理后台'

favicon_view = RedirectView.as_view(url=static_url('favicon.ico'), permanent=True)
robots_view = RedirectView.as_view(url=static_url('robots.txt'), permanent=True)

urlpatterns = [
    re_path(r'^favicon\.ico$', favicon_view),
    re_path(r'^robots\.txt$', robots_view),
    path('', include('pages.urls')),
    path('admin/', admin.site.urls),
    path('martor/', include('martor.urls')),
    path('api/uploader/', markdown_uploader, name='markdown_uploader_page'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    from django.urls import resolve, Resolver404
    try:
        resolve('/static/favicon.ico')
    except Resolver404:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
