from flask import Flask, request
from flask_socketio import SocketIO
from gameManager import GameManager

app = Flask(__name__)
# socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

game_manager = GameManager(socketio)

@app.route("/")
def index():
    return "Chess server is running."

@socketio.on("connect")
def on_connect():
    print("Client connected:", request.sid)
    game_manager.add_user(request.sid)

@socketio.on("message")
def on_message(data):
    game_manager.handle_message(request.sid, data)

@socketio.on("disconnect")
def on_disconnect():
    game_manager.remove_user(request.sid)

# if __name__ == "__main__":
#     socketio.run(app, host='127.0.0.1', port=5000)


if __name__ == "__main__":
    import eventlet
    import eventlet.wsgi
    socketio.run(app, host='0.0.0.0', port=5000)
