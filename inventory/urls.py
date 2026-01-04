from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('buildings/', views.building_list_view, name='buildings'),
    path('new_building/', views.manage_building_users, name='new_building'),
]