from django.urls import path, re_path
from . import views
from .views import UserRegisterView, UserLoginView


urlpatterns = [
    re_path(r'^(?!media/).*$', views.homePage, name='home'),
]



	# path('', views.homePage, name='homePage'),
    # path('login/', views.login, name='login'),
    # path('register/', views.register, name='register'),


	# path('login/', views.login, name='login'),
    # path('register/', views.register, name='register'),

# from django.contrib import admin
# from django.views.generic import RedirectView
# from .views import save_user_profile
# from django.conf import settings
# from django.conf.urls.static import static


	# path('homePage/', views.homePage, name='homePage'),
	# path('error/', views.error, name='error'),
	# path('login/', views.login, name='login'),
	# path('pongGame/', views.pongGame, name='pongGame'),
	# path('leaderboard/', views.leaderboard, name='leaderboard'),
	# path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico')),
	# path('profile/', views.profile, name='profile'),
	# path('settings/', views.settings, name='settings'),
	# path('chat/', views.chat, name='chat'),
	# path('api/save_user_profile/', save_user_profile, name='save_user_profile'),
	# path('get_user/<int:user_id>/', views.get_user, name='get_user'),
	# path('get_user_by_login/<str:login>/', views.get_user_by_login, name='get_user_by_login'),
	# path('get_all_users/', views.get_all_users, name='get_all_users'),
	# path('join_or_create_room/<int:user_id>/<str:room_name>/', views.join_or_create_room, name='join_or_create_room'),