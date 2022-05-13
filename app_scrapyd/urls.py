"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2021/12/5 下午4:30
"""
from django.conf.urls import url
from app_scrapyd import views
from django.urls import path

urlpatterns = [
    url('spider_finished/', views.list_finished),
    url('spider_all/', views.list_spiders),
    url('project_all/', views.project_info),
    url('cancel_spider/', views.cancel_spider),
    url('stats/', views.stats),
    url('check_cancel/', views.check_cancel),
    url('runningTask/', views.RunningTaskCRUD.as_view()),
    url('spiderSetting/', views.SpiderSettingCRUD.as_view()),
    url('spiderStats/', views.SpiderStatsCRUD.as_view())
]
