import json
import traceback
from game import Game
from messages import INIT_GAME, MOVE

class GameManager:
    def __init__(self, socketio):
        self.socketio = socketio
        self.games = []
        self.pending_user = None

    def add_user(self, sid):
        print(f"✅ User connected: {sid}")

    def remove_user(self, sid):
        print(f"❌ User disconnected: {sid}")
        game = self._find_game(sid)
        if game:
            game.end_game(sid)
            self.games.remove(game)
        if self.pending_user == sid:
            self.pending_user = None

    def handle_message(self, sid, data):
        print('📨 Data received:', data)
        try:
            
            # ✅ Parse JSON string if needed
            if isinstance(data, str):
                message = json.loads(data)
            else:
                message = data
                
            mtype = message.get("type")
            payload = message.get("payload", {})
            print("🧩 Message type:", mtype)

            if mtype == INIT_GAME:
                if self.pending_user:
                    game = Game(self.pending_user, sid, self.socketio)
                    self.games.append(game)
                    print('🎮 Starting new game')
                    game.start()
                    self.pending_user = None
                else:
                    self.pending_user = sid

            elif mtype == MOVE:
                print(mtype,payload.get("move"))
                move = payload.get("move")
                game = self._find_game(sid)
                if game:
                    game.make_move(sid, move)

            elif mtype == "message":
                text = payload
                game = self._find_game(sid)
                if game:
                    game.message(sid, text)

        except Exception as e:
            print("⚠️ Error handling message:", e)
            traceback.print_exc()

    def _find_game(self, sid):
        for game in self.games:
            if sid == game.player1 or sid == game.player2:
                return game
        return None
