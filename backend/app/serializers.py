from rest_framework import serializers
from .models import CustomUser
from .models import GameRecord

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'password']
    
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

