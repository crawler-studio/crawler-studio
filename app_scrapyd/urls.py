"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2022/06/15 下午4:30
"""
from django.conf.urls import url
from app_scrapyd import views
from django.urls import path

urlpatterns = [
    url('spiderFinished/', views.FinishTaskCRUD.as_view()),
    url('runningTask/', views.RunningTaskCRUD.as_view()),
    url('spiderStats/', views.SpiderStatsCRUD.as_view()),
]
