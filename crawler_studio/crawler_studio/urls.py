"""crawler_studio_be URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path
from django.conf.urls import include
from rest_framework.authtoken import views
from django.views import static
from django.conf import settings
from django.conf.urls import url
from django.views.generic import TemplateView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/logs/', include('crawler_studio.app_logs.urls')),
    path('api/v1/scrapyd/', include('crawler_studio.app_scrapyd.urls')),
    path('api/v1/settings/', include('crawler_studio.app_settings.urls')),
    path('api/v1/user/', include('crawler_studio.app_user.urls')),
    path('api/v1/api-token-auth/', views.obtain_auth_token),
    path(r'', TemplateView.as_view(template_name="index.html")),
    url(r'^static/(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_ROOT}, name='static'),
]
