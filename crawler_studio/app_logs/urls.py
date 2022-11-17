"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2021/12/5 下午4:30
"""
from django.conf.urls import url
from crawler_studio.app_logs import views

urlpatterns = [
    url('errorLogGroupFromSql/', views.ErrorLogGroupFromSql.as_view()),
    url('errorLogRate/', views.ErrorLogRateCRUD.as_view()),
    url('errorLogContent/', views.ErrorLogContentCRUD.as_view()),
    url('hostErrorLogGroupFromSql/', views.HostErrorLogGroupFromSql.as_view()),
]
