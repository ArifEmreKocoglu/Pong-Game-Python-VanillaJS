from rest_framework import generics, status
from .models import CustomUser
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render



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


class UserLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            print(request.user.is_authenticated)
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

