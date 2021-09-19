from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('characters/<int:character_id>/', views.character_select, name='character_select'),
    path('character/detail/', views.character_detail_view, name='character_detail'),
    path('character/create/', views.character_create_view, name='character_create'),
    path('character/levelup/', views.character_level_up, name='character_level_up'),
    path('character/loot/', views.character_loot, name='character_loot'),
    path('inventory/drop/<int:item_id>', views.inventory_drop, name='inventory_drop'),
    path('map/', views.map_view, name='map'),
    path('locations/<int:location_id>/', views.location_select, name='location_select'),
    path('story/', views.story_view, name='story'),
    path('accounts/signup/', views.signup_view, name='signup'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
]
