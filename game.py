import chess
import json
from messages import INIT_GAME, MOVE, GAME_OVER

class Game:
    def __init__(self, player1, player2, socketio):
        self.player1 = player1
        self.player2 = player2
        self.socketio = socketio
        self.board = chess.Board()
        self.move_count = 0

    def start(self):
        print("🔔 Game started")
        self.socketio.emit("message", json.dumps({
            "type": INIT_GAME,
            "payload": {"color": "w", "id": self.player1}
        }), to=self.player1)

        self.socketio.emit("message", json.dumps({
            "type": INIT_GAME,
            "payload": {"color": "b", "id": self.player2}
        }), to=self.player2)

    def make_move(self, sid, move_data):
        from_square = move_data.get("from")
        to_square = move_data.get("to")
        print("🎃from_square",from_square,to_square)
        if not from_square or not to_square:
            print("returned")
            return

        move_uci = from_square + to_square

        if (self.move_count % 2 == 0 and sid != self.player1) or            (self.move_count % 2 == 1 and sid != self.player2):
            print("🚫 Wrong turn")
            return

        try:
            move = chess.Move.from_uci(move_uci)
            if move in self.board.legal_moves:
                self.board.push(move)
            else:
                print("❌ Illegal move:", move_uci)
                return
        except Exception as e:
            print("❌ Invalid move:", move_uci, e)
            return

        recipient = self.player2 if sid == self.player1 else self.player1
        self.socketio.emit("message", json.dumps({
            "type": MOVE,
            "payload": move_data
        }), to=recipient)

        
        if self.board.is_game_over():
            winner = "black" if self.board.turn == chess.WHITE else "white"
            self.socketio.emit("message", json.dumps({
                "type": GAME_OVER,
                "payload": {"winner": winner}
            }), to=self.player1)
            self.socketio.emit("message", json.dumps({
                "type": GAME_OVER,
                "payload": {"winner": winner}
            }), to=self.player2)
            return

        

        self.move_count += 1

    def message(self, sender_sid, text):
        recipient = self.player2 if sender_sid == self.player1 else self.player1
        self.socketio.emit("message", json.dumps({
            "type": "message_received",
            "payload": {"message": text, "id": sender_sid}
        }), to=recipient)

    def end_game(self, quitter_sid):
        recipient = self.player2 if quitter_sid == self.player1 else self.player1
        self.socketio.emit("message", json.dumps({
            "type": GAME_OVER,
            "payload": {"winner": "opponent quit"}
        }), to=recipient)
