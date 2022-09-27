"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2021/12/5 下午4:30
"""
from django.conf.urls import url
from crawler_studio.app_logs import views

urlpatterns = [
    url('errorLogGroupFromSql/', views.error_log_group_from_sql),
    url('errorLogRate/', views.ErrorLogRateCRUD.as_view()),
    url('errorLogContent/', views.ErrorLogContentCRUD.as_view()),
]
