from flask import Flask
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager


db = SQLAlchemy()


DB_NAME = "database.db"

app = Flask(__name__)
app.config['SECRET_KEY'] = "b'JrarEI9vEBDyNcpUGVmkOfACP44X2NJgzXmJYg3kk1I='"
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

socketio = SocketIO(app)

def create_app():
    # app = Flask(__name__)
    # app.config['SECRET_KEY'] = "b'JrarEI9vEBDyNcpUGVmkOfACP44X2NJgzXmJYg3kk1I='"
    # app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    # socketio = SocketIO(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, ServerList, Server, Category, Channel, Message

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()

    return[app, socketio]