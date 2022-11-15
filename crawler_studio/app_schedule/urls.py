"""
@Description: 
@Usage: 
@Author: liuxianglong
"""
from django.urls import path
from crawler_studio.app_schedule import views

urlpatterns = [
    path('monitorRecipients/', views.MonitorRecipientsCRUD.as_view()),
    path('monitorRules/', views.MonitorRulesCRUD.as_view())
]
