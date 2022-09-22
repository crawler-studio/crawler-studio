"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2021/12/5 下午4:30
"""
from django.conf.urls import url
from crawler_studio.app_logs import views

urlpatterns = [
    url('error_log_group_from_sql/', views.error_log_group_from_sql),
]
