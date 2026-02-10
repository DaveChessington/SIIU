from django.urls import path
from . import views
from .views import UserRegWithRoleAndBuildingView

urlpatterns=[
    path('login',views.LoginView.as_view(),name='login'),
    path('logout',views.logoutView,name='logout'),
    path('profile', views.profileView, name='profile'),
    path('user_list', views.UserListView.as_view(), name='user_list'),
    path('new_user', views.UserRegWithRoleAndBuildingView.as_view(), name='new_user'),
    path('change_user_status/<int:user_id>/', views.changeUserStatus, name='change_user_status'),
    path('change_own_password', views.changeOwnPassword, name='change_own_password'),
]