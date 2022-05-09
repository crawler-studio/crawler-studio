"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2021/12/5 下午4:30
"""
from django.conf.urls import url
from app_docs import views

urlpatterns = [
    url('create/', views.create),
    url('delete/', views.delete),
    url('update/', views.update),
    url('query/', views.query),
    url('get_max_id/', views.get_max_id),
    url('get_doc_type/', views.get_doc_type),
]
