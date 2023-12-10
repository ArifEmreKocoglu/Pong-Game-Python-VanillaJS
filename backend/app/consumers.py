# app/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
# from app.models import CustomUser, GameRecord

waiting_players = set()  # Bağlantıda bekleyen oyuncuları saklamak için bir set

class PongConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        await self.accept()
        waiting_players.add(self)
        await self.match_players()

    async def disconnect(self, close_code):
        waiting_players.discard(self)

    async def match_players(self):
        if len(waiting_players) >= 2:
            player1, player2 = waiting_players.pop(), waiting_players.pop()
            # Eşleşme bilgisini her iki oyuncuya da gönder
            await self.send_to_player(player1, "Eşleşme bulundu, oyun başlıyor.")
            await self.send_to_player(player2, "Eşleşme bulundu, oyun başlıyor.")

    async def send_to_player(self, player, message):
        await player.send(text_data=json.dumps({
            'action': 'matched',
            'message': message
        }))

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')

        if action == 'game_over':
            # Maç sonucu işlemleri
            await self.handle_game_over(text_data_json)

    # @database_sync_to_async
    # def handle_game_over(self, data):
    #     winner_username = data['winner']
    #     loser_username = data['loser']
    #     winner = CustomUser.objects.get(username=winner_username)
    #     loser = CustomUser.objects.get(username=loser_username)
    #     game_record = GameRecord(player1=winner, player2=loser, winner=winner)
    #     game_record.save()
    #     return game_record
