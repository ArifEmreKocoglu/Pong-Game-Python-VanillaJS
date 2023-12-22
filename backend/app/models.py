from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)


class GameRecord(models.Model):
    player1 = models.ForeignKey(CustomUser, related_name='games_player1', on_delete=models.CASCADE)
    player2 = models.ForeignKey(CustomUser, related_name='games_player2', on_delete=models.CASCADE)
    winner = models.ForeignKey(CustomUser, related_name='games_won', on_delete=models.CASCADE, null=True, blank=True)
    loser = models.ForeignKey(CustomUser, related_name='games_lose', on_delete=models.CASCADE, null=True, blank=True)
    loser_score = models.IntegerField(default=0)
    winner_score = models.IntegerField(default=0)
    score_player1 = models.IntegerField(default=0)
    score_player2 = models.IntegerField(default=0)
    game_duration = models.DurationField(null=True, blank=True)
    game_details = models.JSONField(null=True, blank=True)  # Oyunun hareketlerini veya önemli anlarını saklar
    date_played = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('completed', 'Completed'), ('abandoned', 'Abandoned')], default='completed')
