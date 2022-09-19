from django.urls import path
from crawler_studio.app_user import views

urlpatterns = [
    path('register/', views.Register.as_view()),
    path('login/', views.Login.as_view()),
]