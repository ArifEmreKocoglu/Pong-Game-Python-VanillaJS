from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)


class Friendship(models.Model):
    from_user = models.ForeignKey(CustomUser, related_name='friendships_initiated', on_delete=models.CASCADE)
    to_user = models.ForeignKey(CustomUser, related_name='friendships_received', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted')
    )
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='pending')

    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.from_user} to {self.to_user} - {self.status}"

class OnlineStatus(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} is_online: {self.is_online}"



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



class Tournament(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (Created at {self.created_at})"

class TournamentPlayer(models.Model):
    tournament = models.ForeignKey(Tournament, related_name='players', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=255)

    class Meta:
        unique_together = ('tournament', 'user', 'nickname')

    def __str__(self):
        return f"{self.user.username} aka {self.nickname} in {self.tournament.name}"