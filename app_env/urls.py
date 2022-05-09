from django.urls import path
from app_env import views

urlpatterns = [
    path('env/', views.EnvVariableCRUD.as_view()),
]