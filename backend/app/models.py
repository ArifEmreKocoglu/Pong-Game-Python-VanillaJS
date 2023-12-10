from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    pass


class GameRecord(models.Model):
    player1 = models.ForeignKey(CustomUser, related_name='games_player1', on_delete=models.CASCADE)
    player2 = models.ForeignKey(CustomUser, related_name='games_player2', on_delete=models.CASCADE)
    winner = models.ForeignKey(CustomUser, related_name='games_won', on_delete=models.CASCADE)
    date_played = models.DateTimeField(auto_now_add=True)
