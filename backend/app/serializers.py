from rest_framework import serializers
from .models import CustomUser, Friendship
from .models import GameRecord, Tournament, TournamentPlayer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password']
    
    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


class GameRecordSerializer(serializers.ModelSerializer):
    player1_username = serializers.CharField(source='player1.username', read_only=True)
    player2_username = serializers.CharField(source='player2.username', read_only=True)

    class Meta:
        model = GameRecord
        fields = [
            'player1_username', 
            'player2_username', 
            'score_player1', 
            'score_player2', 
            'date_played'
        ]


class FriendshipSerializer(serializers.ModelSerializer):
    from_user = serializers.SlugRelatedField(slug_field='username', queryset=CustomUser.objects.all())
    to_user = serializers.SlugRelatedField(slug_field='username', queryset=CustomUser.objects.all())

    class Meta:
        model = Friendship
        fields = ['id', 'from_user', 'to_user', 'status', 'created_at']
        read_only_fields = ('id', 'created_at', 'from_user')

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['from_user'] = user
        return Friendship.objects.create(**validated_data)

    def validate(self, data):
        if data['to_user'] == data['from_user']:
            raise serializers.ValidationError("Bir kullanıcı kendine arkadaşlık isteği gönderemez.")
        return data


class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = ['id', 'name', 'created_at']  # Burada turnuva ile ilgili diğer alanları ekleyebilirsiniz.

class TournamentPlayerSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')  # Oyuncunun kullanıcı adını gösterir

    class Meta:
        model = TournamentPlayer
        fields = ['id', 'tournament', 'user', 'nickname', 'username']  # Oyuncu ile ilgili diğer alanları ekleyebilirsiniz
        read_only_fields = ['username']  # Kullanıcı adı sadece okunabilir olmalı