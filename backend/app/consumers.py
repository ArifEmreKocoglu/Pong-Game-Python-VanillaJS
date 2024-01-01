# app/consumers.py
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.auth import get_user, get_user_model
from asgiref.sync import sync_to_async


waiting_players = list()

class Player:
    def __init__(self, socket, username, paddle_side=None):
        self.socket = socket
        self.username = username
        self.paddle_side = paddle_side
        self.opponent = None


class PongConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        user = await get_user(self.scope)
        if user.is_authenticated:
            self.username = user.username
            self.player = Player(self, self.username)
            await self.accept()
            waiting_players.append(self.player)
            await self.match_players()
            self.initialize_game()
        else:
            await self.close()


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
        if self.player in waiting_players:
            waiting_players.remove(self.player)

    async def match_players(self):
        if len(waiting_players) >= 2:
            player1 = waiting_players.pop(0)
            player2 = waiting_players.pop(0)
            player1.opponent = player2
            player2.opponent = player1

            await self.notify_players_of_match(player1, player2, "right", "left")
            await self.start_game(player1, player2)

    async def notify_players_of_match(self, player1, player2, player1_paddle, player2_paddle):
        match_message_player1 = {
            'action': 'matched',
            'message': 'Eşleşme bulundu, oyun başlıyor.',
            'paddle': player1_paddle,
            'username': player1.username,
            'opponent_username': player2.username
        }
        match_message_player2 = {
            'action': 'matched',
            'message': 'Eşleşme bulundu, oyun başlıyor.',
            'paddle': player2_paddle,
            'username': player2.username,
            'opponent_username': player1.username 
        }

        player1.paddle_side = player1_paddle
        player2.paddle_side = player2_paddle
        await self.send_to_player(player1, match_message_player1)
        await self.send_to_player(player2, match_message_player2)

    async def start_game(self, player1, player2):
        self.initialize_game()
        game_state = self.get_game_state()
        await self.send_game_state(game_state, player1)
        await self.send_game_state(game_state, player2)
        self.game_task = asyncio.create_task(self.game_loop())


    async def game_loop(self):
        while True:
            try:
                await asyncio.sleep(0.1)
                self.update_ball_position()
                if self.player and self.player.opponent:
                    await self.send_ball_position_to_all() 
                else:
                    break
            except Exception as e:
                print(f"Oyun döngüsünde hata: {e}")
                break

    async def send_ball_position_to_all(self):
        ball_state = {'ball': self.ball}
        if self.player:
            await self.send_to_player(self.player, {'action': 'update_ball', 'state': ball_state})
        if self.player.opponent:
            await self.send_to_player(self.player.opponent, {'action': 'update_ball', 'state': ball_state})



    def update_ball_position(self):
        self.ball['x'] += self.ball_speed['x']
        self.ball['y'] += self.ball_speed['y']
        if self.is_ball_hit_paddle():
            self.ball_speed['x'] *= -1
        if self.ball['y'] - self.ball['radius'] <= 0 or self.ball['y'] + self.ball['radius'] >= self.game_height:
            self.ball_speed['y'] *= -1
        if self.ball['x'] - self.ball['radius'] <= 0:
            self.player_score += 1
            asyncio.create_task(self.notify_score_update())
            self.reset_ball()
        elif self.ball['x'] + self.ball['radius'] >= self.game_width:
            self.opponent_score += 1
            asyncio.create_task(self.notify_score_update())
            self.reset_ball()


    async def notify_score_update(self):
        winning_score = 2
        if self.player_score >= winning_score or self.opponent_score >= winning_score:
            winner_username = self.player.username if self.player_score > self.opponent_score else self.player.opponent.username
            print("Oyun sonlandırılıyor.")
            await self.save_game_result(
                self.player.username,
                self.player.opponent.username,
                self.player_score,
                self.opponent_score
            )
            print("Oyun sonucu kaydedildi.")
            end_game_message = {
                'action': 'end_game',
                'winner': winner_username,
                'player_score': self.player_score,
                'opponent_score': self.opponent_score
            }
            await self.send_to_player(self.player, end_game_message)
            await self.send_to_player(self.player.opponent, end_game_message)
        else:
            # Diğer durumlar için skor güncellemesi
            if self.player and self.player.opponent:
                score_message = {
                    'action': 'update_score',
                    'player_username': self.player.username,
                    'opponent_username': self.player.opponent.username,
                    'player_score': self.player_score,
                    'opponent_score': self.opponent_score
                }
                await self.send_to_player(self.player, score_message)
                await self.send_to_player(self.player.opponent, score_message)

    async def save_game_result(self, player1_username, player2_username, score_player1, score_player2):
        from .models import CustomUser, GameRecord
        try:
            player1 = await database_sync_to_async(CustomUser.objects.get)(username=player1_username)
            player2 = await database_sync_to_async(CustomUser.objects.get)(username=player2_username)
        except CustomUser.DoesNotExist:
            print("Kullanıcı bulunamadı.")
            return None
        game_record = GameRecord(
            player1=player1,
            player2=player2,
            score_player1=score_player1,
            score_player2=score_player2,
            status='completed'
        )
        await database_sync_to_async(game_record.save)()
        return game_record

    def is_ball_hit_paddle(self):
        if self.ball['x'] - self.ball['radius'] <= self.player_paddle['width']:
            if self.ball['y'] >= self.player_paddle['y'] and self.ball['y'] <= self.player_paddle['y'] + self.player_paddle['height']:
                return True
        if self.ball['x'] + self.ball['radius'] >= self.game_width - self.opponent_paddle['width']:
            if self.ball['y'] >= self.opponent_paddle['y'] and self.ball['y'] <= self.opponent_paddle['y'] + self.opponent_paddle['height']:
                return True

        return False
    def reset_ball(self):
        self.ball = {'x': self.game_width // 2, 'y': self.game_height // 2, 'radius': self.ball['radius']}
        self.ball_speed = {'x': -self.ball_speed['x'], 'y': self.ball_speed['y']}

    async def send_game_state_to_all(self):
        game_state = self.get_game_state()
        if self.player:
            await self.send_to_player(self.player, {'action': 'update_state', 'state': game_state})
        if self.player.opponent:
            await self.send_to_player(self.player.opponent, {'action': 'update_state', 'state': game_state})

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


    # receive fonksiyonunu güncelleyin
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')
        direction = text_data_json.get('direction')
        username = text_data_json.get('username')

        if action == 'move_paddle':
            if username == self.player.username:
                self.update_paddle_position(direction, self.player.paddle_side)
            elif self.player.opponent and username == self.player.opponent.username:
                self.update_paddle_position(direction, self.player.opponent.paddle_side)
            await self.send_game_state_to_all()



    async def send_to_player(self, player, message):
        await player.socket.send(text_data=json.dumps(message))

    def update_game_state(self, direction, player_username):
        if player_username == self.player.username:
            self.update_paddle_position(direction, self.player_paddle)
        elif player_username == self.player.opponent.username:
            self.update_paddle_position(direction, self.opponent_paddle)

        return self.get_game_state()

    def update_paddle_position(self, direction, paddle_side):
        if paddle_side == 'right':
            paddle = self.opponent_paddle 
        else:
            paddle = self.player_paddle

        if direction == 'up':
            paddle['y'] = max(paddle['y'] - self.paddle_speed, 0)
        elif direction == 'down':
            paddle['y'] = min(paddle['y'] + self.paddle_speed, self.max_paddle_y)



class FriendshipConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope["user"].id  # Kullanıcının ID'si
        self.room_group_name = f"user_{self.user_id}"  # Kullanıcıya özel grup adı

        # Kullanıcıyı kendi özel grubuna kat
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Kullanıcıyı grubundan çıkar
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Bu fonksiyon, arkadaşlık isteği gönderildiğinde çağrılacak
    async def friend_request(self, event):
        # Gönderen kullanıcının bilgilerini al
        from_user_id = event["from_user_id"]
        from_user_username = event["from_user_username"]
        friendship_id = event["friendship_id"]

        # Hedef kullanıcıya bildirimi gönder
        await self.send(text_data=json.dumps({
            'action': 'friend_request',
            'from_user_id': from_user_id,
            'friendship_id': friendship_id,
            'from_user_username': from_user_username
        }))

    async def friend_request_response(self, event):
        response = event["response"]
        to_user_username = event["to_user_username"]
        friendship_id = event["friendship_id"]
        from_user_id = event["from_user_id"]

        # Gönderen kullanıcıya bildirimi gönder
        await self.send(text_data=json.dumps({
            'action': 'friend_request_response',
            'response': response,
            'from_user_id': from_user_id,
            'friendship_id': friendship_id,
            'to_user_username': to_user_username
        }))

    async def websocket_send(self, event):
        await self.send(text_data=event["text"])

    async def accept_friend_request(self, event):
        friendship_id = event['friendship_id']
        from_user_id = event['from_user_id']
        to_user_id = event['to_user_id']
 
        await self.send(text_data=json.dumps({
            'action': 'accept_friend_request',
            'message': 'Arkadaşlık isteği kabul edildi.',
            'friendship_id': friendship_id,
            'from_user_id': from_user_id
        }))

    async def reject_friend_request(self, event):

        friendship_id = event['friendship_id']
        from_user_id = event['from_user_id']  
 
        await self.send(text_data=json.dumps({
            'action': 'reject_friend_request',
            'message': 'Arkadaşlık isteği reddedildi.',
            'friendship_id': friendship_id,
            'from_user_id': from_user_id
        }))




# TURNUVAAAAAAAAAAAA


class TournamentConsumer(AsyncWebsocketConsumer):
  
    async def connect(self):
        # Kullanıcıyı turnuva güncellemeleri grubuna ekleyin
        await self.channel_layer.group_add("tournament_updates", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Kullanıcıyı gruptan çıkarın
        await self.channel_layer.group_discard("tournament_updates", self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['action']
        
        if action == 'create_tournament':
            tournament_name = text_data_json['name']
            nickname = text_data_json['nickname']  # Kullanıcıdan gelen nickname
            user = self.scope["user"]  # WebSocket bağlantısının sahibi olan kullanıcı
            
            # Yeni turnuva oluştur ve turnuva oluşturanı katılımcı olarak ekle
            tournament = await self.create_tournament(tournament_name, user, nickname)
            
            # Tüm bağlantılara yeni turnuva bilgisini gönder
            await self.channel_layer.group_send(
                "tournament_updates",
                {
                    "type": "send_tournament_update",
                    "tournament": {
                        "id": tournament.id,
                        "name": tournament.name,
                    }
                }
            )

    @database_sync_to_async
    def create_tournament(self, name, user, nickname):
        from .models import Tournament, TournamentPlayer
        tournament = Tournament.objects.create(name=name)
        TournamentPlayer.objects.create(tournament=tournament, user=user, nickname=nickname)
        return tournament

    async def send_tournament_update(self, event):
        await self.send(text_data=json.dumps({
            'action': 'tournament_update',
            'tournament': event['tournament']
        }))