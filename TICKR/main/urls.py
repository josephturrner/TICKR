from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('insights/<str:symbol>/', views.insights, name='insights'),
]
