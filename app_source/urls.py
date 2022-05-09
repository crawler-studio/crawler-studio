"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2022/1/16 上午1:03
"""
from django.urls import path
from app_source import views

urlpatterns = [
    path('category/<type>/', views.CategoryCRUD.as_view()),
    path('source/<type>/', views.SourceCRUD.as_view()),
    path('topic/', views.SourceTopicCRUD.as_view()),
    path('state/', views.SourceStateCRUD.as_view()),
]
