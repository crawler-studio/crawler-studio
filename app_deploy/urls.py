"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2021/12/14 下午7:10
"""

from django.conf.urls import url
from app_deploy import views

urlpatterns = [
    url('pull', views.pull),

]
