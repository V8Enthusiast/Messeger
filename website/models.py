from . import db
from flask_login import UserMixin
from sqlalchemy import func

class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    servers = db.relationship('ServerList', back_populates='user')
    messages = db.relationship('Message', back_populates='user')
    handle = db.Column(db.Integer, unique=True)
    description = db.Column(db.String(2500))
    instagram = db.Column(db.String(150))
    instagram_link = db.Column(db.String(150))
    facebook = db.Column(db.String(150))
    facebook_link = db.Column(db.String(150))
    youtube = db.Column(db.String(150))
    youtube_link = db.Column(db.String(150))
    twitter = db.Column(db.String(150))
    twitter_link = db.Column(db.String(150))
    discord = db.Column(db.String(150))
    discord_link = db.Column(db.String(150))
    github = db.Column(db.String(150))
    github_link = db.Column(db.String(150))
    other_socials = db.Column(db.String(1500))
    can_be_added_by_id = db.Column(db.Boolean, default=True)
    can_be_direct_messaged = db.Column(db.Boolean, default=True)
    def get_id(self):
           return (self.user_id)

class ServerList(db.Model):
    __tablename__ = 'serverlist'
    server_list_id = db.Column(db.Integer, primary_key=True)
    kicked = db.Column(db.Boolean, default=False)
    banned = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'))
    user = db.relationship('User', back_populates='servers')
    #servers = db.relationship('Server', back_populates='serverlist')

class Server(db.Model):
    __tablename__ = 'server'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(150), unique=True)
    name = db.Column(db.String(150))
    default_channel_id = db.Column(db.Integer)
    can_join_by_code = db.Column(db.Boolean, default=True)

    directMessage = db.Column(db.Boolean, default=False)
    dm_user1_id = db.Column(db.Integer)
    dm_user2_id = db.Column(db.Integer)

    owner = db.Column(db.Integer)
    serverlist_id = db.Column(db.Integer, db.ForeignKey('serverlist.server_list_id'))
    #serverlist = db.relationship('ServerList', back_populates='servers')
    categories = db.relationship('Category', back_populates='server')

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'))
    server = db.relationship('Server', back_populates='categories')
    channels = db.relationship('Channel', back_populates='category')

class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', back_populates='channels')
    messages = db.relationship('Message', back_populates='channel')
    isLiveChannel = db.Column(db.Boolean, default=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(10000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    user = db.relationship('User', back_populates='messages')
    time = db.Column(db.DateTime(timezone=True), default=func.now())
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'))
    channel = db.relationship('Channel', back_populates='messages')
