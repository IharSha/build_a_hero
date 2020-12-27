from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('characters/<int:character_id>/', views.character_detail, name='character_detail'),
    path('character_create/', views.character_create_view, name='character_create'),
    path(
        'characters/<int:character_id>/levelup/',
        views.character_level_up,
        name='character_level_up'
    ),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
