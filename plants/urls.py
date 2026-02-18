# plants/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.user_registration, name='user_registration'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # plants CRUD
    path('plants/', views.plant_list, name='plant_list'),
    path('plants/add/', views.plant_create, name='plant_create'),
    path('plants/<int:pk>/edit/', views.plant_update, name='plant_update'),
    path('plants/<int:pk>/delete/', views.plant_delete, name='plant_delete'),

    # schedule actions
    path('schedule/<int:pk>/toggle/', views.schedule_toggle_done, name='schedule_toggle_done'),
]
