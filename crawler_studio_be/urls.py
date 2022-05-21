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
# from app_schedule.views import TimerScheduler


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/scrapyd/', include('app_scrapyd.urls')),
    path('api/v1/deploy/', include('app_deploy.urls')),
    path('api/v1/settings/', include('app_settings.urls')),
    path('api/v1/docs/', include('app_docs.urls')),
    path('api/v1/user/', include('app_user.urls')),
    path('api/v1/logs/', include('app_logs.urls')),
    path('api/v1/dashboard/', include('app_dashboard.urls')),
    path('api/v1/schedule/', include('app_schedule.urls')),
]