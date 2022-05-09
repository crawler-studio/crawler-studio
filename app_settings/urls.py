"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2021/12/16 下午12:53
"""
from django.conf.urls import url
from app_settings import views

urlpatterns = [
    url('scrapydserver/', views.ScrapydServerAddr.as_view()),
    url('logserver/', views.LogServerAddr.as_view()),
    url('gitlab/', views.Gitlab.as_view())
]
