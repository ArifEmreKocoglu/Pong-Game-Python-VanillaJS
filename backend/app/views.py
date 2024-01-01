import logging
import asyncio
from django.shortcuts import render, redirect
from rest_framework import generics, status
from .models import CustomUser, GameRecord, Friendship, OnlineStatus, Tournament, TournamentPlayer
from .serializers import UserSerializer, GameRecordSerializer, TournamentSerializer
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from channels.db import database_sync_to_async
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from .forms import CustomUserForm
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from django.contrib.auth import get_user




def homePage(request):
    path = request.path
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if path.startswith('/login'):
            return render(request, 'login.html')
        elif path.startswith('/register'):
            return render(request, 'register.html')
        elif path.startswith('/user-page'):
            if request.user.is_authenticated:
                return render(request, 'user-page.html')
            else:
                return HttpResponse(status=401) 
        elif path.startswith('/game'):
            return render(request, 'pong.html')
        elif path.startswith('/multi-game'):
            if request.user.is_authenticated:
                return render(request, 'multi-game.html')
            else:
                return HttpResponse(status=401)
        elif path.startswith('/match-history'):
            if request.user.is_authenticated:
                return render(request, 'match-history.html')
            else:
                return HttpResponse(status=401)
        elif path.startswith('/tournament-page'):
            if request.user.is_authenticated:
                return render(request, 'tournament-page.html')
            else:
                return HttpResponse(status=401)
        else:
            return render(request, 'index.html')

    return render(request, 'index.html')

class GameResultsView(APIView):
    authentication_classes = [SessionAuthentication]
    def post(self, request):
        data = request.data

        player1_username = data.get('player1Username')
        player2_username = data.get('player2Username')
        try:
            player1 = CustomUser.objects.get(username=player1_username)
            player2 = CustomUser.objects.get(username=player2_username)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Oyuncu bulunamadı.'}, status=status.HTTP_400_BAD_REQUEST)

        game_record = GameRecord(
            player1=player1,
            player2=player2,
            score_player1=data.get('scorePlayer1'),
            score_player2=data.get('scorePlayer2'),
            date_played=timezone.now(),
            status='completed'
        )
        game_record.save()

        return Response({'message': 'Oyun kaydedildi.'}, status=status.HTTP_201_CREATED)


class UserGameHistoryView(APIView):
    authentication_classes = [SessionAuthentication]
    def get(self, request):
        print(request.user.is_authenticated)
        if not request.user.is_authenticated:
            return Response({'error': 'Kullanıcı girişi gereklidir.'}, status=status.HTTP_401_UNAUTHORIZED)

        user_games = GameRecord.objects.filter(player1=request.user) | GameRecord.objects.filter(player2=request.user)
        user_games = user_games.order_by('-date_played')
        serializer = GameRecordSerializer(user_games, many=True)
        print(serializer.data)
        return Response(serializer.data)

class UserRegisterView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def post(self, request):

        user = self.create(request)

        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return Response({'message': 'Üyelik ve oturum açma başarılı.'})
        else:
            return Response({'error': 'Kullanıcı adı veya şifre hatalı.'}, status=status.HTTP_401_UNAUTHORIZED)


class UserLoginView(APIView):
    authentication_classes = [TokenAuthentication]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return Response({'message': 'Oturum açma başarılı.'})
        else:
            return Response({'error': 'Kullanıcı adı veya şifre hatalı.'}, status=status.HTTP_401_UNAUTHORIZED)



class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    def post(self, request):
        logout(request)
        return Response({'message': 'Çıkış yapıldı'}, status=status.HTTP_200_OK)



class UploadAvatarView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        form = CustomUserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save()
            if user.avatar:
                avatar_url = user.avatar.url
            else:
                avatar_url = 'path/to/default/avatar.png'
            avatar_url = request.build_absolute_uri(avatar_url)
            return Response({'avatarUrl': avatar_url}, status=status.HTTP_200_OK)
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)




class ListUsersView(APIView):
    authentication_classes = [SessionAuthentication]
    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class FriendsListView(APIView):
    authentication_classes = [SessionAuthentication]
    def get(self, request):
        friendships = Friendship.objects.filter(
            (Q(from_user=request.user) | Q(to_user=request.user)) & Q(status='accepted')
        )
        friends_data = [{
            'username': friendship.to_user.username if friendship.from_user == request.user else friendship.from_user.username,
            'friendship_id': friendship.id  # Friendship ID'yi ekleyin
        } for friendship in friendships]

        return Response(friends_data, status=status.HTTP_200_OK)

class DeleteFriendshipView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, friendship_id):
        try:
            # Arkadaşlık ilişkisini bul ve sil
            friendship = Friendship.objects.get(id=friendship_id)
            from_user_id = friendship.from_user.id
            to_user_id = friendship.to_user.id
            friendship.delete()

            channel_layer = get_channel_layer()

            # Her iki kullanıcıya da mesaj gönder
            common_message = {
                "type": "websocket.send",
                "text": json.dumps({
                    "action": "friendship_deleted",
                    "friendship_id": friendship_id,
                    "message": "Arkadaşlık ilişkisi silindi."
                })
            }

            async_to_sync(channel_layer.group_send)(f"user_{from_user_id}", common_message)

            async_to_sync(channel_layer.group_send)(f"user_{to_user_id}", common_message)

            return Response({'message': 'Arkadaşlık ilişkisi başarıyla silindi.'}, status=status.HTTP_200_OK)
        except Friendship.DoesNotExist:
            return Response({'error': 'Arkadaşlık ilişkisi bulunamadı veya zaten silinmiş.'}, status=status.HTTP_404_NOT_FOUND)


class SendFriendRequestView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        # Hedef kullanıcıyı bul
        try:
            target_user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Kullanıcı bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)

        # Eğer kullanıcılar zaten arkadaşsa veya istek reddedilmişse, yeni istek gönderilmez
        if Friendship.objects.filter(from_user=request.user, to_user=target_user, status='accepted').exists() \
           or Friendship.objects.filter(from_user=target_user, to_user=request.user, status='accepted').exists():
            return Response({'message': 'Kullanıcılar zaten arkadaş.'}, status=status.HTTP_409_Conflict)

        # Arkadaşlık isteği oluştur veya mevcut 'pending' durumdakini güncelle
        friendship, created = Friendship.objects.update_or_create(
            from_user=request.user,
            to_user=target_user,
            defaults={'status': 'pending'}
        )
        print(friendship.id)
        # Arkadaşlık isteğini hedef kullanıcıya WebSocket üzerinden bildir
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{target_user.id}",
            {
                "type": "friend_request",
                "friendship_id": friendship.id,
                "from_user_id": request.user.id,
                "to_user_id": target_user.id,
                "from_user_username": request.user.username
            }
        )
        return Response({'message': 'Arkadaşlık isteği gönderildi veya güncellendi.'}, status=status.HTTP_201_CREATED)


class AcceptFriendRequestView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, friendship_id):
        try:
            friendship = Friendship.objects.get(id=friendship_id, to_user=request.user, status='pending')
            from_user = friendship.from_user
            to_user = request.user

            friendship.status = 'accepted'
            friendship.save()

            channel_layer = get_channel_layer()

            # İstek alan (to_user) kullanıcıya mesaj gönder
            async_to_sync(channel_layer.group_send)(
                f"user_{to_user.id}",
                {
                    "type": "websocket.send",
                    "text": json.dumps({
                        "action": "friend_request_accepted",
                        "friendship_id": friendship.id,
                        "from_user_id": from_user.id,
                        "from_user_username": from_user.username,
                        "to_user_id": to_user.id
                    })
                }
            )

            # İstek gönderen (from_user) kullanıcıya mesaj gönder
            async_to_sync(channel_layer.group_send)(
                f"user_{from_user.id}",
                {
                    "type": "websocket.send",
                    "text": json.dumps({
                        "action": "friend_request_accepted",
                        "friendship_id": friendship.id,
                        "to_user_id": to_user.id,
                        "to_user_username": to_user.username,
                        "from_user_id": from_user.id
                    })
                }
            )

            return Response({'message': 'Arkadaşlık isteği kabul edildi.'}, status=status.HTTP_200_OK)
        except Friendship.DoesNotExist:
            return Response({'error': 'Arkadaşlık isteği bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)

class DeleteFriendRequestView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, friendship_id):
        try:
            friendship = Friendship.objects.get(id=friendship_id, to_user=request.user, status='pending')
            friendship.delete()
            return Response({'message': 'Arkadaşlık isteği silindi.'}, status=status.HTTP_204_NO_CONTENT)
        except Friendship.DoesNotExist:
            return Response({'error': 'Arkadaşlık isteği bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)

class UpdateOnlineStatusView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_status, _ = OnlineStatus.objects.get_or_create(user=request.user)
        user_status.is_online = True
        user_status.last_seen = timezone.now()
        user_status.save()
        return Response({'message': 'Çevrimiçi durum güncellendi.'}, status=status.HTTP_200_OK)


class ListFriendsOnlineStatusView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        friendships = Friendship.objects.filter(to_user=request.user, status='accepted')
        friends_online_status = []

        for friendship in friendships:
            friend = friendship.from_user
            online_status = OnlineStatus.objects.get(user=friend)
            friends_online_status.append({
                'friend_username': friend.username,
                'is_online': online_status.is_online,
                'last_seen': online_status.last_seen
            })

        return Response(friends_online_status, status=status.HTTP_200_OK)

class FriendRequestsListView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        friend_requests = Friendship.objects.filter(to_user=request.user, status='pending')
        requests_data = [{
            'friendship_id': frequest.id,
            'from_user_id': frequest.from_user.id,
            'from_user_username': frequest.from_user.username
        } for frequest in friend_requests]
        return Response(requests_data, status=status.HTTP_200_OK)










class JoinTournamentView(APIView):
    def post(self, request):
        user = get_user(request)
        tournament_id = request.data.get('tournamentId')
        nickname = request.data.get('nickname')
        
        try:
            tournament = Tournament.objects.get(id=tournament_id)
            if TournamentPlayer.objects.filter(tournament=tournament, nickname=nickname).exists():
                return Response({"error": "This nickname is already taken for this tournament."}, status=status.HTTP_400_BAD_REQUEST)

            TournamentPlayer.objects.create(tournament=tournament, user=user, nickname=nickname)
            return Response({"message": "Successfully joined the tournament!"})

        except Tournament.DoesNotExist:
            return Response({"error": "Tournament not found."}, status=status.HTTP_404_NOT_FOUND)

class UserParticipationsView(APIView):
    authentication_classes = [SessionAuthentication]
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(status=403)

        participations = TournamentPlayer.objects.filter(user=request.user)

        data = [{'tournamentId': participation.tournament.id, 'tournamentName': participation.tournament.name} for participation in participations]
        return Response(data)

class TournamentListView(APIView):
    authentication_classes = [SessionAuthentication]
    def get(self, request):
        tournaments = Tournament.objects.all()
        serializer = TournamentSerializer(tournaments, many=True)
        return Response(serializer.data)

class TournamentParticipantsView(APIView):
    def get(self, request, tournament_id):
        participants = TournamentPlayer.objects.filter(tournament__id=tournament_id)
        participants_data = [
            {"id": participant.id, "nickname": participant.nickname, "user": participant.user.username}
            for participant in participants
        ]
        return Response(participants_data)

class ExitTournamentView(APIView):
    def post(self, request, tournament_id):
        # Kullanıcının bu turnuvadaki katılımcısını bul
        participant = get_object_or_404(TournamentPlayer, tournament__id=tournament_id, user=request.user)
        participant.delete()
        return Response({"message": "Successfully exited the tournament."})

from django.http import HttpResponse
