import logging
from django.shortcuts import render, redirect
from rest_framework import generics, status
from .models import CustomUser, GameRecord
from .serializers import UserSerializer, GameRecordSerializer
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


from django.http import HttpResponse
