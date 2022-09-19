"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2022/6/16 下午12:53
"""
from django.conf.urls import url
from crawler_studio.app_settings import views

urlpatterns = [
    url('scrapydserver/', views.ScrapydServerAddr.as_view()),
    url('logserver/', views.LogServerAddr.as_view()),
]
