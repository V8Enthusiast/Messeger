from website import create_app
from flask_socketio import join_room, leave_room, send, SocketIO
app1 = create_app()
app = app1[0]
socketio = app1[1]

if __name__ == '__main__':
    socketio.run(app, debug=True,allow_unsafe_werkzeug=True)