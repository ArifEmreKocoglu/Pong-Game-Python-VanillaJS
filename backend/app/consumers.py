# app/consumers.py
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
# from app.models import CustomUser, GameRecord

waiting_players = set()  # Bağlantıda bekleyen oyuncuları saklamak için bir set

class Player:
    def __init__(self, socket, username):
        self.socket = socket
        self.username = username
        self.opponent = None

# PongConsumer düzenlemesi
class PongConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        username = "admin"  # Kullanıcı adı; bu kısmı dinamik hale getirin
        self.player = Player(self, username)
        await self.accept()
        waiting_players.add(self.player)
        await self.match_players()
        self.initialize_game()  # Oyunu başlat


    def initialize_game(self):
        self.ball = {'x': 100, 'y': 100, 'radius': 10}
        self.ball_speed = {'x': 10, 'y': 10}
        self.player_paddle = {'y': 50, 'height': 100, 'width': 10}
        self.opponent_paddle = {'y': 150, 'height': 100, 'width': 10}
        self.player_score = 0
        self.opponent_score = 0
        self.paddle_speed = 10
        self.game_width = 800
        self.game_height = 400
        self.paddle_height = 100
        self.max_paddle_y = self.game_height - self.paddle_height

    async def disconnect(self, close_code):
        waiting_players.discard(self.player)

    async def match_players(self):
        if len(waiting_players) >= 2:
            player1, player2 = waiting_players.pop(), waiting_players.pop()
            player1.opponent = player2
            player2.opponent = player1
            # Oyunculara eşleşme bilgisini gönder
            await self.notify_players_of_match(player1, player2)
            # İlk oyun durumunu gönder
            await self.start_game(player1, player2)

    async def notify_players_of_match(self, player1, player2):
        match_message = {
            'action': 'matched',
            'message': 'Eşleşme bulundu, oyun başlıyor.'
        }
        await self.send_to_player(player1, match_message)
        await self.send_to_player(player2, match_message)

    async def start_game(self, player1, player2):
        self.initialize_game()
        self.game_task = asyncio.create_task(self.game_loop())

    async def game_loop(self):
        while True:
            try:
                await asyncio.sleep(0.1)  # Oyun durumunu her 0.1 saniyede bir güncelle
                self.update_ball_position()
                # self.update_game_state('none')
                if self.player and self.player.opponent:
                    print("selam")
                    await self.send_game_state_to_all()
                else:
                    break  # Oyun döngüsünü durdur eğer bir oyuncu ayrılmışsa
            except Exception as e:
                print(f"Oyun döngüsünde hata: {e}")
                break  # Hata oluşursa döngüyü sonlandır

    def update_ball_position(self):
        # Topun pozisyonunu güncelle
        self.ball['x'] += self.ball_speed['x']
        self.ball['y'] += self.ball_speed['y']

        # Topun oyuncu çubuklarına çarpma kontrolü
        if self.is_ball_hit_paddle():
            self.ball_speed['x'] *= -1

        # Topun alt ve üst sınırlara çarpması durumunda yön değiştir
        if self.ball['y'] - self.ball['radius'] <= 0 or self.ball['y'] + self.ball['radius'] >= self.game_height:
            self.ball_speed['y'] *= -1

        # Skor güncellemesi ve topun sınırlara çarpması durumunda yön değiştir
        if self.ball['x'] - self.ball['radius'] <= 0:
            self.opponent_score += 1
            self.reset_ball()
        elif self.ball['x'] + self.ball['radius'] >= self.game_width:
            self.player_score += 1
            self.reset_ball()

    def is_ball_hit_paddle(self):
        # Topun oyuncu çubuklarına çarpıp çarpmadığını kontrol et
        # Oyuncu çubuğu için çarpışma kontrolü
        if self.ball['x'] - self.ball['radius'] <= self.player_paddle['width']:
            if self.ball['y'] >= self.player_paddle['y'] and self.ball['y'] <= self.player_paddle['y'] + self.player_paddle['height']:
                return True

        # Rakip çubuğu için çarpışma kontrolü
        if self.ball['x'] + self.ball['radius'] >= self.game_width - self.opponent_paddle['width']:
            if self.ball['y'] >= self.opponent_paddle['y'] and self.ball['y'] <= self.opponent_paddle['y'] + self.opponent_paddle['height']:
                return True

        return False
    def reset_ball(self):
        # Topun pozisyonunu oyun alanının ortasına sıfırla ve yönünü değiştir
        self.ball = {'x': self.game_width // 2, 'y': self.game_height // 2, 'radius': self.ball['radius']}
        self.ball_speed = {'x': -self.ball_speed['x'], 'y': self.ball_speed['y']}

    async def send_game_state_to_all(self):
        game_state = self.get_game_state()
        await self.send_game_state(game_state, self.player)
        if self.player.opponent:
            await self.send_game_state(game_state, self.player.opponent)

    def get_game_state(self):
        return {
            'ball': self.ball,
            'player_paddle': self.player_paddle,
            'opponent_paddle': self.opponent_paddle,
            'player_score': self.player_score,
            'opponent_score': self.opponent_score
        }
        
    async def send_game_state(self, game_state, player):
        await player.socket.send(text_data=json.dumps({
            'action': 'update_state',
            'state': game_state
        }))

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')

        if action == 'move_paddle':
            direction = text_data_json.get('direction')
            game_state = self.update_game_state(direction)
            # Her iki oyuncuya da oyunun güncel durumunu gönder
            await self.send_game_state(game_state, self.player)
            if self.player.opponent:
                await self.send_game_state(game_state, self.player.opponent)

    async def send_to_player(self, player, message):
        await player.socket.send(text_data=json.dumps(message))

    def update_game_state(self, direction):

        # Paddle hareketlerini güncelle
        if direction == 'up':
            self.player_paddle['y'] = max(self.player_paddle['y'] - self.paddle_speed, 0)
        elif direction == 'down':
            self.player_paddle['y'] = min(self.player_paddle['y'] + self.paddle_speed, self.max_paddle_y)

        return {
            'ball': self.ball,
            'player_paddle': self.player_paddle,
            'opponent_paddle': self.opponent_paddle,
            'player_score': self.player_score,
            'opponent_score': self.opponent_score
        }