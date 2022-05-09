"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2021/12/5 下午4:30
"""
from django.conf.urls import url
from app_logs import views

urlpatterns = [
    url('search/', views.search),
    url('log_analysis/', views.analysis_spider_error_log_out),
    url('group_error_log/', views.group_error_log)
]
