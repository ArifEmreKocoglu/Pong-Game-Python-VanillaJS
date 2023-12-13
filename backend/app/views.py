import logging
from django.shortcuts import render, redirect
from rest_framework import generics, status
from .models import CustomUser
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


# # 42 API
# API_URL = "https://api.intra.42.fr/oauth/authorize?client_id=u-s4t2ud-4bc482d21834a4addd9108c8db4a5f99efb73b172f1a4cb387311ee09a26173c&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fcheck_authorize%2F&response_type=code"
# API_URR = "https://api.intra.42.fr/oauth/authorize?client_id=u-s4t2ud-4bc482d21834a4addd9108c8db4a5f99efb73b172f1a4cb387311ee09a26173c&redirect_uri=https%3A%2F%2Flocalhost%3A8000%2Fcheck_authorize%2F&response_type=code"
# API_URU = "https://api.intra.42.fr/oauth/authorize?client_id=u-s4t2ud-4bc482d21834a4addd9108c8db4a5f99efb73b172f1a4cb387311ee09a26173c&redirect_uri=https%3A%2F%2Flocalhost%3A8000%2Fcheck_authorize%2F&response_type=code"
# API_USER = 'https://api.intra.42.fr/v2/me'
# token = '690c107e335181f7039f3792799aebb1fa4d55b320bd232dd68877c0cc13545d'


def homePage(request):
    path = request.path
    print(path)
    print(request.user.is_authenticated)
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
        else:
            return render(request, 'index.html')

    return render(request, 'index.html')



class UserRegisterView(generics.CreateAPIView):
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




# class UserLoginView(APIView):
#     def post(self, request):
#         username = request.data.get('username')
#         password = request.data.get('password')

#         user = authenticate(username=username, password=password)

#         if user:
#             login(request, user)
#             print(request.user.is_authenticated)
#             return Response({'message': 'Oturum açma başarılı.'})
#         else:
#             return Response({'error': 'Kullanıcı adı veya şifre hatalı.'}, status=status.HTTP_401_UNAUTHORIZED)




class UserLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)

            # Kullanıcı adını ve ID'sini WebSocket bağlantısına gönder
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_add)("pong_game", self.channel_name)
            async_to_sync(channel_layer.group_send)(
                "pong_game",
                {
                    "type": "user.login",
                    "username": username,
                    "user_id": user.id,
                },
            )

            return Response({'message': 'Oturum açma başarılı.'})
        else:
            return Response({'error': 'Kullanıcı adı veya şifre hatalı.'}, status=status.HTTP_401_UNAUTHORIZED)



class LogoutView(APIView):
    def post(self, request):
        print(request.user.is_authenticated)
        logout(request)
        print(request.user.is_authenticated)
        return Response({'message': 'Çıkış yapıldı'}, status=status.HTTP_200_OK)


from django.http import HttpResponse

