"""
@Description: 
@Usage: 
@Author: liuxianglong
"""
from django.conf.urls import url
from crawler_studio.app_scrapyd import views
from django.urls import path

urlpatterns = [
    url('spiderFinished/', views.FinishTaskCRUD.as_view()),
    url('runningTask/', views.RunningTaskCRUD.as_view()),
    url('spiderStats/', views.SpiderStatsCRUD.as_view()),
    url('spiderStartParams/', views.SpiderStartParamsCRUD.as_view()),
    url('newTask/', views.NewTaskCRUD.as_view())
]
