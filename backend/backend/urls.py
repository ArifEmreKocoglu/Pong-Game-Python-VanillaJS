"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from app.views import UserRegisterView, UserLoginView, LogoutView, UserGameHistoryView, GameResultsView, UploadAvatarView, SendFriendRequestView, AcceptFriendRequestView, DeleteFriendRequestView, UpdateOnlineStatusView, ListFriendsOnlineStatusView, ListUsersView, FriendsListView, DeleteFriendshipView, FriendRequestsListView, TournamentListView, UserParticipationsView, JoinTournamentView, TournamentParticipantsView, ExitTournamentView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('api/game-results/', GameResultsView.as_view(), name='game-results'),
    path('api/match-history/', UserGameHistoryView.as_view(), name='match-history'),
    path('api/register/', UserRegisterView.as_view(), name='user-register'),
    path('api/login/', UserLoginView.as_view(), name='user-login'), 
    path('api/logout/', LogoutView.as_view(), name='logout'), 
    path('api/upload-avatar/', UploadAvatarView.as_view(), name='upload-avatar'),

    path('api/users/', ListUsersView.as_view(), name='list-users'),
    path('api/send-friend-request/<int:user_id>/', SendFriendRequestView.as_view(), name='send-friend-request'),
    path('api/accept-friend-request/<int:friendship_id>/', AcceptFriendRequestView.as_view(), name='accept-friend-request'),
    path('api/delete-friend-request/<int:friendship_id>/', DeleteFriendRequestView.as_view(), name='delete-friend-request'),
    path('api/delete-friendship/<int:friendship_id>/', DeleteFriendshipView.as_view(), name='delete-friendship'),
    path('api/update-online-status/', UpdateOnlineStatusView.as_view(), name='update-online-status'),
    path('api/friend-requests/', FriendRequestsListView.as_view(), name='friend-requests'),
    path('api/friends-list/', FriendsListView.as_view(), name='friends-list'),
    path('api/list-friends-online-status/', ListFriendsOnlineStatusView.as_view(), name='list-friends-online-status'),

    path('api/tournaments/', TournamentListView.as_view(), name='tournament-list'),
    path('api/user_participations/', UserParticipationsView.as_view(), name='user_participations'),
    path('api/join_tournament/', JoinTournamentView.as_view(), name='join_tournament'),
    path('api/tournaments/<int:tournament_id>/participants/', TournamentParticipantsView.as_view(), name='tournament_participants'),
    path('api/tournaments/<int:tournament_id>/exit/', ExitTournamentView.as_view(), name='exit_tournament'),




    # path('api/create_tournaments/', CreateTournamentView.as_view(), name='create-tournament'),

    path('', include('app.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)