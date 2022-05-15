"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2021/12/5 下午4:30
"""
from django.urls import path
from django.conf.urls import url
from app_schedule import views


urlpatterns = [
    # path('timerTask/', views.TimerScheduler.as_view()),
    path('monitorRecipients/', views.MonitorRecipientsCRUD.as_view()),
    path('monitorRules/', views.MonitorRulesCRUD.as_view())
]
