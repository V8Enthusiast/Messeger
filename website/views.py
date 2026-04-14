from flask import Blueprint, render_template, request, redirect, url_for, make_response, flash, session
from flask_login import login_required, current_user
from flask_socketio import join_room, leave_room, send, close_room, SocketIO
from .models import User, ServerList, Server, Category, Channel, Message
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, socketio

views = Blueprint('views', __name__)


def verifyUserAccess(server_id):
    serverLists = ServerList.query.filter_by(user_id=current_user.user_id).all()
    serverIds = []
    for serverList in serverLists:
        serverIds.append(serverList.server_id)

    if server_id not in serverIds:
        #flash("You do not have permission to access that server!", category='Error')
        return False
    return True


@views.route('/home')
@login_required
def home():
    serverLists = ServerList.query.filter_by(user_id=current_user.user_id).all()
    returnString = ""
    serverIds = []
    for serverList in serverLists:
        if serverList.banned is not True:
            serverIds.append(serverList.server_id)

    servers = []

    for id in serverIds:
        servers.append(Server.query.filter_by(id=id).first())

    for server in servers:
        if server.directMessage is False:
            returnString += "<a id=\"menuitem\" href=\"/server?id=" + str(server.id) + "\">"+ str(server.name) +"</a><br>"
        else:
                user1 = User.query.filter_by(user_id=server.dm_user1_id).first()
                user2 = User.query.filter_by(user_id=server.dm_user2_id).first()
                if current_user == user1:
                    returnString += "<a id=\"menuitem\" href=\"/server?id=" + str(server.id) + "\">"+ user2.name +"</a><br>"
                else:
                    returnString += "<a id=\"menuitem\" href=\"/server?id=" + str(server.id) + "\">"+ user1.name +"</a><br>"

    messageButton = "<a href=\"/edit-profile\"><button class=\"menubtn\">Edit profile</button></a>"
    user = current_user
    instagram = ""
    facebook = ""
    youtube = ""
    discord = ""
    twitter = ""
    github = ""
    description = user.description
    if description == None or description == "":
        description = "Hey, I'm using Messeger!"
    if user.instagram_link is not None and user.instagram_link != "https://instagram.com/":
        instagram = "<a href=\"" + str(user.instagram_link) + "\" target=\"_blank\"><div class=\"image\"><img src=\"/static/img/instagram.png\" style=\"height:80px\"><div class=\"descriptiontext\"><button type=\"button\">@" + str(user.instagram) +"</button></div></div></a>"
    if user.facebook_link is not None and user.facebook_link != "https://facebook.com/":
        facebook = "<a href=\"" + str(user.facebook_link) + "\" target=\"_blank\"><div class=\"image\"><img src=\"/static/img/facebook.png\" style=\"height:80px\"><div class=\"descriptiontext\"><button type=\"button\">@" + str(user.facebook) +"</button></div></div></a>"
    if user.youtube_link is not None and user.youtube_link != "https://youtube.com/":
        youtube = "<a href=\"" + str(user.youtube_link) + "\" target=\"_blank\"><div class=\"image\"><img src=\"/static/img/youtube.png\" style=\"height:80px\"><div class=\"descriptiontext\"><button type=\"button\">@" + str(user.youtube) +"</button></div></div></a>"
    if user.discord_link is not None and user.discord_link != "https://discordapp.com/users/":
        discord = "<a href=\"" + str(user.discord_link) + "\" target=\"_blank\"><div class=\"image\"><img src=\"/static/img/discord.png\" style=\"height:80px\"><div class=\"descriptiontext\"><button type=\"button\">@" + str(user.discord) +"</button></div></div></a>"
    if user.twitter_link is not None and user.twitter_link != "https://twitter.com/":
        twitter = "<a href=\"" + str(user.twitter_link) + "\" target=\"_blank\"><div class=\"image\"><img src=\"/static/img/twitter.png\" style=\"height:80px\"><div class=\"descriptiontext\"><button type=\"button\">@" + str(user.twitter) +"</button></div></div></a>"
    if user.github_link is not None and user.github_link != "https://github.com/":
        github = "<a href=\"" + str(user.github_link) + "\" target=\"_blank\"><div class=\"image\"><img src=\"/static/img/github.png\" style=\"height:80px\"><div class=\"descriptiontext\"><button type=\"button\">@" + str(user.github) +"</button></div></div></a>"
    other_socials = user.other_socials
    if other_socials is None:
        other_socials = "No other social links"

    return render_template("home.html", chats=returnString, user=current_user, name=user.name, messagebtn=messageButton, description=description, instagram=instagram, twitter=twitter, facebook=facebook, youtube=youtube, discord=discord, github=github, other_socials=other_socials)

@views.route('/')
def home2():
    if current_user.is_authenticated:
        return redirect(url_for("views.home"))
    return render_template("home_logged_out.html", chats="", user="")
@views.route('/create-server', methods=['GET', 'POST'])
@login_required
def new_server():
    if request.method == "POST":
        user = current_user
        code = request.form.get("server_id")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if join != False and not code:
            return render_template("new_server.html", chats="", user="", error="Please enter a server ID")
        if join != False:
            server = Server.query.filter_by(code=code).first()
            if server is None or server.directMessage is True:
                return render_template("new_server.html", chats="", user="", error="Please enter a valid server code")
            if server.can_join_by_code is False:
                return render_template("new_server.html", chats="", user="", error="This server does not allow joining by code")
            else:
                serverlist = ServerList.query.filter_by(user_id=current_user.user_id, server_id=server.id).first()
                if serverlist is not None:
                    if serverlist.banned is False:
                        return render_template("new_server.html", chats="", user="", error="You are already in that server")
                    else:
                        return render_template("new_server.html", chats="", user="", error="You have been banned from that server!")
                new_server_list = ServerList(user_id=current_user.user_id, server_id=server.id)
                db.session.add(new_server_list)
                db.session.commit()

                return redirect(url_for('views.home'))
            
        if create != False:
            server = Server.query.filter_by(code=code).first()
            if server is not None:
                return render_template("new_server.html", chats="", user="", error="This server code is already taken")
            else:
                new_server = Server(code=code, name=code, owner=current_user.user_id)
                db.session.add(new_server)
                db.session.commit()

                new_category = Category(name=code, server_id=new_server.id)
                db.session.add(new_category)
                db.session.commit()
                
                new_channel = Channel(name="General", category_id=new_category.id)
                db.session.add(new_channel)
                db.session.commit()

                new_server.default_channel_id = new_channel.id

                new_server_list = ServerList(user_id=current_user.user_id, server_id=new_server.id)
                db.session.add(new_server_list)
                db.session.commit()

                return redirect(url_for('views.home'))
    return render_template("new_server.html", chats="", user="")

@views.route('/new-direct-message', methods=['GET', 'POST'])
@login_required
def new_direct_message():
    label = ""
    if request.method == 'GET':
        user_handle = request.args.get('user')
        if user_handle is not None:
            verified = True
            for char in user_handle:
                if char not in "0123456789":
                    verified = False
            if verified is True and len(user_handle) > 1:
                label = user_handle
    if request.method == 'POST':
        form_handle = request.form.get("user_id")
        if form_handle is not None:
            verified = True
            for char in form_handle:
                if char not in "0123456789":
                    verified = False
            if verified is False or len(form_handle) <= 1:
                flash("Incorrect user ID", category='Error')
                return redirect(url_for("views.new_direct_message"))
        # server_handle = str(generate_password_hash(str(current_user.handle) + form_handle, 'sha256'))
        # server_handle2 = str(generate_password_hash(form_handle + str(current_user.handle), 'sha256'))
        server_handle = str(current_user.handle) + form_handle
        server_handle2 = form_handle + str(current_user.handle)
        temp1 = Server.query.filter_by(code=server_handle).first()
        temp2 = Server.query.filter_by(code=server_handle2).first()
        print(temp1)
        user2 = User.query.filter_by(handle=form_handle).first()
        if user2 is None:
            flash("Incorrect user ID", category='Error')
            return redirect(url_for("views.new_direct_message"))
        if temp1 is not None or temp2 is not None:
            flash("This conversation already exists!", category='Error')
            return redirect(url_for("views.new_direct_message"))
        else:
            if user2.can_be_direct_messaged is True:
                temp = Server(code=server_handle, directMessage=True, dm_user1_id=current_user.user_id, dm_user2_id=user2.user_id, name="Direct Message")
                db.session.add(temp)
                db.session.commit()

                new_category = Category(name="Direct Message", server_id=temp.id)
                db.session.add(new_category)
                db.session.commit()
                
                new_channel = Channel(name="Chat", category_id=new_category.id)
                db.session.add(new_channel)
                db.session.commit()

                temp.default_channel_id = new_channel.id

                new_channel2 = Channel(name="Live chat", category_id=new_category.id, isLiveChannel=True)
                db.session.add(new_channel2)
                db.session.commit()

                new_server_list = ServerList(user_id=current_user.user_id, server_id=temp.id)
                db.session.add(new_server_list)
                db.session.commit()

                new_server_list = ServerList(user_id=user2.user_id, server_id=temp.id)
                db.session.add(new_server_list)
                db.session.commit()
                return redirect(url_for("views.home"))
            else:
                flash("This user can't be direct messaged", category='Error')
                return redirect(url_for("views.new_direct_message"))

    return render_template("new_direct_message.html", label=label)

@views.route('/server', methods=['GET', 'POST'])
@login_required
def server():
    session.clear()
    requested_channel_id = None
    if request.method == 'GET':
        server_id = request.args['id']
        server_id = int(server_id)
    if request.method == 'POST':
        leave_button = request.form.get("leave")
        if leave_button is None:
            requested_channel_id = request.form.get("channel")
            requested_channel_id = int(requested_channel_id)
            temp_category_id = Channel.query.filter_by(id=requested_channel_id).first().category_id
            server_id = Category.query.filter_by(id=temp_category_id).first().server_id
        else:
            server_id = request.args['id']
            server_id = int(server_id)

    current_server = Server.query.filter_by(id=server_id).first()

    if request.method == 'POST':
        leave_button = request.form.get("leave")
        if leave_button is not None:
            server_list_to_delete = ServerList.query.filter_by(user_id=current_user.user_id, server_id=current_server.id).first()
            if server_list_to_delete is not None:
                db.session.delete(server_list_to_delete)
                db.session.commit()
                flash("Successfully left the server!", category='success')
                return redirect(url_for("views.home"))

    if requested_channel_id is None:
            requested_channel_id = current_server.default_channel_id

    serverLists = ServerList.query.filter_by(user_id=current_user.user_id).all()
    returnString = ""
    serverIds = []
    for serverList in serverLists:
        if serverList.banned is not True:
            serverIds.append(serverList.server_id)

    if server_id not in serverIds:
        flash("You do not have permission to access that server!", category='Error')
        return redirect(url_for("views.home"))

    else:
        servers = []

        for id in serverIds:
            servers.append(Server.query.filter_by(id=id).first())

        DBcategories = Category.query.filter_by(server_id=server_id).all()

        lefttext = ""
        startChannel = 0
        for category in DBcategories:
            category_id = category.id
            DBchannels = Channel.query.filter_by(category_id=category_id).all()
            lefttext += "<br><h2 class=\"fancyText2\">" + str(category.name) + "</h2><br>"
            print(lefttext)
            for channel in DBchannels:
                startChannel = channel.id
                lefttext += "<button type=\"submit\" name=\"channel\" value=\"" + str(channel.id) + "\">#" + str(channel.name) +"</button><br>"
                
        lefttext += "<input type=\"hidden\" name=\"defaultChannelId\" value=\"" + str(startChannel) + "\">"

        session["server"] = server_id
        if requested_channel_id is None:
            session["channel"] = startChannel
            channel_id = startChannel
        else:
            session["channel"] = requested_channel_id
            channel_id = requested_channel_id

        messages = ""

        DBMessages = Message.query.filter_by(channel_id=channel_id).all() 

        last_user = None
        for message in DBMessages:
            if message.user != current_user:
                if message.user == last_user:
                    messages += f"<div class=\"text\"style=\"margin-top:3px;\"><a><span><strong class=\"fancyText\">{(message.user.name).split(' ')[0]}:</strong> {message.text}&nbsp;&nbsp;&nbsp;</span><div class=\"muted\"><br>Sent:&nbsp;{message.time}</div></a></div>"
                else:
                    messages += f"<div class=\"text\"><a><span><strong class=\"fancyText\">{(message.user.name).split(' ')[0]}:</strong> {message.text}&nbsp;&nbsp;&nbsp;</span><div class=\"muted\"><br>Sent:&nbsp;{message.time}</div></a></div>"
            else:
                if message.user == last_user:
                    messages += f"<br><div class=\"text\" style=\"background-color:purple;margin-top:3px;text-align: left;display: inline-block;\"><a><span><strong class=\"fancyText\">{(message.user.name).split(' ')[0]}:</strong> {message.text}&nbsp;&nbsp;&nbsp;</span><div class=\"muted\"><br>Sent:&nbsp;{message.time}</div></a></div>"
                else:
                    messages += f"<br><div class=\"text\" style=\"background-color:purple;text-align: left;display: inline-block;\"><a><span><strong class=\"fancyText\">{(message.user.name).split(' ')[0]}:</strong> {message.text}&nbsp;&nbsp;&nbsp;</span><div class=\"muted\"><br>Sent:&nbsp;{message.time}</div></a></div>"
            last_user = message.user

        session["name"] = current_user.name
        for server in servers:
            if server.directMessage is False:
                returnString += "<a id=\"menuitem\" href=\"/server?id=" + str(server.id) + "\">"+ str(server.name) +"</a><br>"
            else:
                    user1 = User.query.filter_by(user_id=server.dm_user1_id).first()
                    user2 = User.query.filter_by(user_id=server.dm_user2_id).first()
                    if current_user == user1:
                        returnString += "<a id=\"menuitem\" href=\"/server?id=" + str(server.id) + "\">"+ user2.name +"</a><br>"
                    else:
                        returnString += "<a id=\"menuitem\" href=\"/server?id=" + str(server.id) + "\">"+ user1.name +"</a><br>"

        editbtn = ""
        if current_server.owner == current_user.user_id:
            editbtn = "<a href=\"/edit-server?id=" + str(current_server.id) + "\"><button class=\"menubtn\" style=\"width:fit-content; padding:10px; margin-bottom:0px\">Edit server settings</button></a>"
        
        DBserverlists = ServerList.query.filter_by(server_id=server_id).all()
        members = ""
        if current_server.directMessage is False:
            server_owner = User.query.filter_by(user_id=current_server.owner).first()
            for serverlist in DBserverlists:
                user = serverlist.user
                if serverlist.banned is True:
                    continue
                elif user == current_user and current_user.user_id != current_server.owner:
                    members += "<div class=\"text\" style=\"background-color:transparent; margin-top:0px; padding-top:0px; margin-left:0px; padding-left:0px; padding-bottom:0px\"><a href=\"profile?user=" + str(user.handle) + "\" target=\"_blank\"><button type=\"button\">" + user.name + "</button></a><div class=\"muted\"><button style=\"font-size:18px; margin-right:2px\" type=\"submit\" name=\"leave\" value=\"" + str(user.user_id) + "\">Leave Server</button></div></div>"
                elif user != server_owner:
                    members += "<a href=\"profile?user=" + str(user.handle) + "\" target=\"_blank\"><button type=\"button\">" + user.name + "</button></a><br>"
            members = "<a href=\"profile?user=" + str(server_owner.handle) + "\" target=\"_blank\"><button type=\"button\" style=\"background: linear-gradient(90deg, rgba(131,58,180,1) 0%, rgba(253,29,29,1) 50%, rgba(252,176,69,1) 100%); font-weight:bold; color:pink\">" + server_owner.name + " (Admin)</button></a><br>" + members
        else:
            user1 = User.query.filter_by(user_id=current_server.dm_user1_id).first()
            user2 = User.query.filter_by(user_id=current_server.dm_user2_id).first()
            members = "<a href=\"profile?user=" + str(user1.handle) + "\" target=\"_blank\"><button type=\"button\">" + user1.name + "</button></a><br>" + "<a href=\"profile?user=" + str(user2.handle) + "\" target=\"_blank\"><button type=\"button\">" + user2.name + "</button></a><br>"
        return render_template("server.html", chats=returnString, user=current_user, server_name=current_server.name, channels=lefttext, dbmessages=messages, editbtn=editbtn, members=members)

@views.route('/edit-server', methods=['GET', 'POST'])
@login_required
def server_edit():
    session.clear()
    requested_channel_id = None
    if request.method == 'GET':
        server_id = request.args['id']
        server_id = int(server_id)
    if request.method == 'POST':
        requested_channel_id = request.form.get("channel")
        if requested_channel_id is None:
            requested_channel_id = request.form.get("defaultChannelId")
        requested_channel_id = int(requested_channel_id)
        temp_category_id = Channel.query.filter_by(id=requested_channel_id).first().category_id
        server_id = Category.query.filter_by(id=temp_category_id).first().server_id

    current_server = Server.query.filter_by(id=server_id).first()
    Error = False
    ErrorMsg = ""

    serverLists = ServerList.query.filter_by(user_id=current_user.user_id).all()
    returnString = ""
    serverIds = []
    for serverList in serverLists:
        if serverList.banned is not True:
            serverIds.append(serverList.server_id)

    if server_id not in serverIds:
        flash("You do not have permission to access that server!", category='Error')
        return redirect(url_for("views.home"))

    else:
        if current_user.user_id == current_server.owner:
            servers = []
            
            kicked_user = request.form.get("kick")
            banned_user = request.form.get("ban")
            if kicked_user is not None:
                kicked_user = int(kicked_user)
                server_list_to_burn = ServerList.query.filter_by(server_id=current_server.id, user_id=kicked_user).first()
                #server_list_to_burn.kicked = True
                #db.session.commit()
                db.session.delete(server_list_to_burn)
                db.session.commit()
            if banned_user is not None:
                banned_user = int(banned_user)
                server_list_to_burn = ServerList.query.filter_by(server_id=current_server.id, user_id=banned_user).first()
                server_list_to_burn.banned = True
                db.session.commit()
                #db.session.delete(server_list_to_burn)
                #db.session.commit()

            new_live_channel = request.form.get("makelive")
            if new_live_channel is not None:
                live_channel = Channel.query.filter_by(id=int(new_live_channel)).first()
                if live_channel is not None:
                    live_channel.isLiveChannel = True
                    messages_to_delete = Message.query.filter_by(channel_id=live_channel.id)
                    for message in messages_to_delete:
                        db.session.delete(message)
                    db.session.commit()
            new_normal_channel = request.form.get("makenormal")
            if new_normal_channel is not None:
                normal_channel = Channel.query.filter_by(id=int(new_normal_channel)).first()
                if normal_channel is not None:
                    normal_channel.isLiveChannel = False
                    db.session.commit()
            new_default_channel = request.form.get("makedefault")
            if new_default_channel is not None:
                default_channel = Channel.query.filter_by(id=int(new_default_channel)).first()
                if default_channel is not None:
                    current_server.default_channel_id = default_channel.id
                    db.session.commit()

            channel_to_remove_id = request.form.get("removechannel")
            if channel_to_remove_id is not None:
                channel_to_remove = Channel.query.filter_by(id=int(channel_to_remove_id)).first()
                if channel_to_remove is not None and channel_to_remove.id != current_server.default_channel_id:
                    messages_to_delete = Message.query.filter_by(channel_id=channel_to_remove.id)
                    for message in messages_to_delete:
                        db.session.delete(message)
                    db.session.delete(channel_to_remove)
                    db.session.commit()
            
            category_to_remove_id = request.form.get("removecategory")
            if category_to_remove_id is not None:
                category_to_remove = Category.query.filter_by(id=int(category_to_remove_id)).first()
                if category_to_remove is not None:
                    DBchannels = Channel.query.filter_by(category_id=category_to_remove.id).all()
                    canRemoveCategory = True
                    for channel in DBchannels:
                        if channel.id == current_server.default_channel_id:
                            canRemoveCategory = False
                    if canRemoveCategory:
                        for channel in DBchannels:
                            db.session.delete(channel)
                        db.session.delete(category_to_remove)
                        db.session.commit()

            for id in serverIds:
                servers.append(Server.query.filter_by(id=id).first())

            if request.method == 'POST':
                adduser = request.form.get("add-user", False)
                userid = request.form.get("user-id", False)
                if adduser != False and userid is not None:
                    verified = True
                    for char in userid:
                        if char not in "0123456789":
                            verified = False
                    if verified and len(userid) == 8:
                        user = User.query.filter_by(handle=int(userid)).first()
                        if user is not None:
                            temp_serverlist = ServerList.query.filter_by(server_id=current_server.id, user_id=user.user_id).first()
                            if temp_serverlist is not None and temp_serverlist.banned is False:
                                Error = True
                                ErrorMsg = "The user you are trying to add is already in the server"
                            else:
                                if user.can_be_added_by_id is True:
                                    new_serverlist = ServerList(server_id=current_server.id, user_id=user.user_id)
                                    db.session.add(new_serverlist)
                                    db.session.commit()
                                else:
                                    Error = True
                                    ErrorMsg = "This user can't be added by id"
                        else:
                            Error = True
                            ErrorMsg = "The user you are trying to add doesn't exist"
                    else:
                        Error = True
                        ErrorMsg = "Please enter a valid user ID"
                else:
                    server_name = request.form.get("serverName")
                    if server_name != current_server.name:
                        current_server.name = server_name
                        db.session.commit()
                    DBcategories = Category.query.filter_by(server_id=server_id).all()
                    for category in DBcategories:
                        new_name = request.form.get(str(category.id))
                        category.name = new_name
                        db.session.commit()
                        DBchannels = Channel.query.filter_by(category_id=category.id).all()
                        for channel in DBchannels:
                            new_name = request.form.get("channel" + str(channel.id))
                            channel.name = new_name
                            db.session.commit()
                        new_channel_name = request.form.get("newchannel" + str(category.id))
                        if new_channel_name != "New Channel":
                            new_channel = Channel(name=new_channel_name, category_id=category.id)
                            db.session.add(new_channel)
                            db.session.commit()
                    new_category_name = request.form.get("newcategory")
                    if new_category_name != "New Category":
                        new_category = Category(name=new_category_name, server_id=server_id)
                        db.session.add(new_category)
                        db.session.commit()
                    allow_joining_by_code = request.form.get("allow-code")
                    if allow_joining_by_code != current_server.can_join_by_code:
                        if allow_joining_by_code:
                            current_server.can_join_by_code = True
                        else:
                            current_server.can_join_by_code = False
                        db.session.commit()


            DBcategories = Category.query.filter_by(server_id=server_id).all()

            lefttext = ""
            startChannel = 0
            for category in DBcategories:
                category_id = category.id
                DBchannels = Channel.query.filter_by(category_id=category_id).all()
                canRemoveCategory = True
                for channel in DBchannels:
                    if channel.id == current_server.default_channel_id:
                        canRemoveCategory = False
                if canRemoveCategory:
                    lefttext += "<br><div class=\"text\" style=\"background-color:transparent; margin-top:0px; padding-top:0px; margin-left:0px; padding-left:0px\"><input type=\"text\" name=\"" + str(category.id) + "\" value=\"" + str(category.name) + "\" style=\"font-size:32px;;border-radius:10px\"><div class=\"muted\"><button style=\"font-size:18px; margin-right:2px; margin-left:10px;margin-top:5px\" type=\"submit\" name=\"removecategory\" value=\"" + str(category.id) + "\">Remove</button></div></div>"
                else:
                    lefttext += "<br><input type=\"text\" name=\"" + str(category.id) + "\" value=\"" + str(category.name) + "\" style=\"font-size:32px;;border-radius:10px\"><br><br>"
                for channel in DBchannels:
                    # if kicked_user is not None:
                    #     close_room(channel.id)
                    startChannel = channel.id
                    if channel.id == current_server.default_channel_id and channel.isLiveChannel is False:
                        lefttext += "<div class=\"text\" style=\"background-color:transparent; margin-top:0px; padding-top:0px; margin-left:0px; padding-left:0px\"><input type=\"text\" name=\"channel" + str(channel.id) + "\" value=\"" + str(channel.name) + "\" style=\"font-size:24px;border-radius:10px\"><div class=\"muted\"><button style=\"font-size:18px; margin-right:2px; margin-left:10px;margin-top:5px\" type=\"submit\" name=\"makelive\" value=\"" + str(channel.id) + "\">Make live channel</button></div></div>"
                    elif channel.id == current_server.default_channel_id:
                        lefttext += "<div class=\"text\" style=\"background-color:transparent; margin-top:0px; padding-top:0px; margin-left:0px; padding-left:0px\"><input type=\"text\" name=\"channel" + str(channel.id) + "\" value=\"" + str(channel.name) + "\" style=\"font-size:24px;border-radius:10px\"><div class=\"muted\"><button style=\"font-size:18px; margin-right:2px; margin-left:10px;margin-top:5px\" type=\"submit\" name=\"makenormal\" value=\"" + str(channel.id) + "\">Disable live</button></div></div>"
                    if channel.isLiveChannel is False and channel.id != current_server.default_channel_id:
                        lefttext += "<div class=\"text\" style=\"background-color:transparent; margin-top:0px; padding-top:0px; margin-left:0px; padding-left:0px\"><input type=\"text\" name=\"channel" + str(channel.id) + "\" value=\"" + str(channel.name) + "\" style=\"font-size:24px;border-radius:10px\"><div class=\"muted\"><button style=\"font-size:18px; margin-right:2px; margin-left:10px;margin-top:5px\" type=\"submit\" name=\"makedefault\" value=\"" + str(channel.id) + "\">Set as default</button><button style=\"font-size:18px; margin-left:10px; margin-right:2px\" type=\"submit\" name=\"makelive\" value=\"" + str(channel.id) + "\">Make live channel</button><button style=\"font-size:18px; margin-left:10px; margin-right:0px\" type=\"submit\" name=\"removechannel\" value=\"" + str(channel.id) + "\">Remove</button></div></div>"
                    elif channel.id != current_server.default_channel_id:
                        lefttext += "<div class=\"text\" style=\"background-color:transparent; margin-top:0px; padding-top:0px; margin-left:0px; padding-left:0px\"><input type=\"text\" name=\"channel" + str(channel.id) + "\" value=\"" + str(channel.name) + "\" style=\"font-size:24px;border-radius:10px\"><div class=\"muted\"><button style=\"font-size:18px; margin-right:2px; margin-left:10px;margin-top:5px\" type=\"submit\" name=\"makedefault\" value=\"" + str(channel.id) + "\">Set as default</button><button style=\"font-size:18px; margin-left:10px; margin-right:2px\" type=\"submit\" name=\"makenormal\" value=\"" + str(channel.id) + "\">Disable live</button><button style=\"font-size:18px; margin-left:10px; margin-right:0px\" type=\"submit\" name=\"removechannel\" value=\"" + str(channel.id) + "\">Remove</button></div></div>"
                lefttext += "<input type=\"text\" name=\"newchannel" + str(category_id) + "\" value=\"New Channel\" style=\"font-size:24px;border-radius:10px;\"><br>"
            lefttext += "<br><input type=\"text\" name=\"newcategory\" value=\"New Category\" style=\"font-size:32px;;border-radius:10px\"><br><br><button class=\"menubtn\" style=\"width:fit-content; padding:10px; margin-bottom:0px\" type=\"submit\">Save Changes</button>"
            lefttext += "<input type=\"hidden\" name=\"defaultChannelId\" value=\"" + str(startChannel) + "\">"
            session["server"] = server_id
            if requested_channel_id is None:
                session["channel"] = startChannel
                channel_id = startChannel
            else:
                session["channel"] = requested_channel_id
                channel_id = requested_channel_id

            center_text = ""

            if current_server.can_join_by_code is True:
                center_text = "<center><p style=\"font-size:32px\">Allow joining by code <input type=\"checkbox\" name=\"allow-code\" class=\"checkbox\" style=\"height:42px;width:42px; bottom:-11px;\" checked></p></center>"
            else:
                center_text = "<center><p style=\"font-size:32px\">Allow joining by code <input type=\"checkbox\" name=\"allow-code\" class=\"checkbox\" style=\"height:42px;width:42px; bottom:-11px;\"></p></center>"
            
            center_text += "<center><button class=\"menubtn\" style=\"width:fit-content; padding:10px; margin-bottom:0px\" type=\"submit\">Save Changes</button></center>"
            # DBMessages = Message.query.filter_by(channel_id=channel_id).all() 

            # last_user = None
            # for message in DBMessages:
            #     if message.user != current_user:
            #         if message.user == last_user:
            #             messages += f"<div class=\"text\"style=\"margin-top:0px;\"><span><strong class=\"fancyText\">{(message.user.name).split(' ')[0]}:</strong> {message.text}&nbsp;&nbsp;&nbsp;</span><br><span class=\"muted\">Read:&nbsp;{message.time}</span></div>"
            #         else:
            #             messages += f"<div class=\"text\"><span><strong class=\"fancyText\">{(message.user.name).split(' ')[0]}:</strong> {message.text}&nbsp;&nbsp;&nbsp;</span><br><span class=\"muted\">Read:&nbsp;{message.time}</span></div>"
            #     else:
            #         if message.user == last_user:
            #             messages += f"<div class=\"text\" style=\"background-color:purple;margin-top:0px;\"><span><strong class=\"fancyText\">{(message.user.name).split(' ')[0]}:</strong> {message.text}&nbsp;&nbsp;&nbsp;</span><br><span class=\"muted\">Read:&nbsp;{message.time}</span></div>"
            #         else:
            #             messages += f"<div class=\"text\" style=\"background-color:purple;\"><span><strong class=\"fancyText\">{(message.user.name).split(' ')[0]}:</strong> {message.text}&nbsp;&nbsp;&nbsp;</span><br><span class=\"muted\">Read:&nbsp;{message.time}</span></div>"
            #     last_user = message.user

            session["name"] = current_user.name
            for server in servers:
                if server.directMessage is False:
                    returnString += "<a id=\"menuitem\" href=\"/server?id=" + str(server.id) + "\">"+ str(server.name) +"</a><br>"
                else:
                        user1 = User.query.filter_by(user_id=server.dm_user1_id).first()
                        user2 = User.query.filter_by(user_id=server.dm_user2_id).first()
                        if current_user == user1:
                            returnString += "<a id=\"menuitem\" href=\"/server?id=" + str(server.id) + "\">"+ user2.name +"</a><br>"
                        else:
                            returnString += "<a id=\"menuitem\" href=\"/server?id=" + str(server.id) + "\">"+ user1.name +"</a><br>"

            editbtn = "<a href=\"/server?id=" + str(current_server.id) + "\"><button type=\"button\" class=\"menubtn\" style=\"width:fit-content; padding:10px; margin-bottom:0px\">Back to server</button></a>"
            server_input_box = "<form method=\"POST\"><input type=\"text\" name=\"serverName\" value=\"" + str(current_server.name) +"\" style=\"font-size:24px;border-radius:10px;\">"
            
            new_admin = request.form.get("makeadmin")
            print("|",new_admin,"|")
            #print(int(new_admin))
            if new_admin is not None:
                current_server.owner = int(new_admin)
                db.session.commit()
                flash("You are no longer the admin", category='Error')
                return redirect(url_for("views.home"))

            DBserverlists = ServerList.query.filter_by(server_id=server_id).all()
            members = ""
            server_owner = User.query.filter_by(user_id=current_server.owner).first()
            for serverlist in DBserverlists:
                user = serverlist.user
                if serverlist.banned is True:
                    continue
                elif user != server_owner:
                    members += "<div class=\"text\" style=\"background-color:transparent; margin-top:0px; padding-top:0px; margin-left:0px; padding-left:0px\"><a href=\"profile?user=" + str(user.handle) + "\" target=\"_blank\"><button type=\"button\">" + user.name + "</button></a><div class=\"muted\"><button style=\"font-size:18px; margin-right:2px\" type=\"submit\" name=\"makeadmin\" value=\"" + str(user.user_id) + "\">Make admin</button><button style=\"font-size:18px; margin-left:10px; margin-right:2px\" type=\"submit\" name=\"kick\" value=\"" + str(user.user_id) + "\">Kick</button><button style=\"font-size:18px; margin-left:10px; margin-right:0px\" type=\"submit\" name=\"ban\" value=\"" + str(user.user_id) + "\">Ban</button></div></div>"
            members = "<a href=\"profile?user="+ str(server_owner.handle) + "\" target=\"_blank\"><button type=\"button\" style=\"background: linear-gradient(90deg, rgba(131,58,180,1) 0%, rgba(253,29,29,1) 50%, rgba(252,176,69,1) 100%); font-weight:bold; color:pink\">" + server_owner.name + " (Admin)</button></a><br>" + members

            if Error:
                return render_template("server_edit.html", chats=returnString, user=current_user, server_name=server_input_box, channels=lefttext, dbmessages=center_text, editbtn=editbtn, members=members, error=ErrorMsg)
            return render_template("server_edit.html", chats=returnString, user=current_user, server_name=server_input_box, channels=lefttext, dbmessages=center_text, editbtn=editbtn, members=members)

        else:
            flash("You do not have permission to edit that server!", category='Error')
            return redirect(url_for("views.home"))

@views.route('/profile', methods=['GET'])
@login_required
def profile():
    if request.method == 'GET':
        user_handle = request.args.get("user")
        if user_handle is not None:
            user_handle = int(user_handle)
            user = User.query.filter_by(handle=user_handle).first()
            messageButton = "<a href=\"/new-direct-message?user=" + str(user_handle) + "\"><button class=\"menubtn\">Message</button></a>"
            if user_handle == current_user.handle:
                ### This should return the editable version of the current_user profile ###
                messageButton = "<a href=\"/edit-profile\"><button class=\"menubtn\">Edit profile</button></a>"
                user = current_user

        else:
            ### This should return the editable version of the current_user profile ###
            messageButton = "<a href=\"/edit-profile\"><button class=\"menubtn\">Edit profile</button></a>"
            user = current_user
        instagram = ""
        facebook = ""
        youtube = ""
        discord = ""
        twitter = ""
        github = ""
        description = user.description
        if description == None or description == "":
            description = "Hey, I'm using Messeger!"
        if user.instagram_link is not None and user.instagram_link != "https://instagram.com/":
            instagram = "<a href=\"" + str(user.instagram_link) + "\" target=\"_blank\"><div class=\"image\"><img src=\"/static/img/instagram.png\" style=\"height:80px\"><div class=\"descriptiontext\"><button type=\"button\">@" + str(user.instagram) +"</button></div></div></a>"
        if user.facebook_link is not None and user.facebook_link != "https://facebook.com/":
            facebook = "<a href=\"" + str(user.facebook_link) + "\" target=\"_blank\"><div class=\"image\"><img src=\"/static/img/facebook.png\" style=\"height:80px\"><div class=\"descriptiontext\"><button type=\"button\">@" + str(user.facebook) +"</button></div></div></a>"
        if user.youtube_link is not None and user.youtube_link != "https://youtube.com/":
            youtube = "<a href=\"" + str(user.youtube_link) + "\" target=\"_blank\"><div class=\"image\"><img src=\"/static/img/youtube.png\" style=\"height:80px\"><div class=\"descriptiontext\"><button type=\"button\">@" + str(user.youtube) +"</button></div></div></a>"
        if user.discord_link is not None and user.discord_link != "https://discordapp.com/users/":
            discord = "<a href=\"" + str(user.discord_link) + "\" target=\"_blank\"><div class=\"image\"><img src=\"/static/img/discord.png\" style=\"height:80px\"><div class=\"descriptiontext\"><button type=\"button\">@" + str(user.discord) +"</button></div></div></a>"
        if user.twitter_link is not None and user.twitter_link != "https://twitter.com/":
            twitter = "<a href=\"" + str(user.twitter_link) + "\" target=\"_blank\"><div class=\"image\"><img src=\"/static/img/twitter.png\" style=\"height:80px\"><div class=\"descriptiontext\"><button type=\"button\">@" + str(user.twitter) +"</button></div></div></a>"
        if user.github_link is not None and user.github_link != "https://github.com/":
            github = "<a href=\"" + str(user.github_link) + "\" target=\"_blank\"><div class=\"image\"><img src=\"/static/img/github.png\" style=\"height:80px\"><div class=\"descriptiontext\"><button type=\"button\">@" + str(user.github) +"</button></div></div></a>"
        other_socials = user.other_socials
        if other_socials is None:
            other_socials = "No other social links"
        
        return render_template("profile.html",name=user.name, messagebtn=messageButton, description=description, instagram=instagram, twitter=twitter, facebook=facebook, youtube=youtube, discord=discord, github=github, other_socials=other_socials)
@views.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def profile_edit():
    if request.method == 'POST':
        allow_adding = request.form.get("allow-add")
        if allow_adding != current_user.can_be_added_by_id:
            current_user.can_be_added_by_id = bool(allow_adding)
            db.session.commit()
        allow_dming = request.form.get("allow-dm")
        if allow_dming != current_user.can_be_direct_messaged:
            current_user.can_be_direct_messaged = bool(allow_dming)
            db.session.commit()
        description = request.form.get('description')
        if description != current_user.description:
            current_user.description = description
            db.session.commit()
        instagram = request.form.get("instagram")
        if instagram != current_user.instagram:
            current_user.instagram = instagram
            if "/" in instagram:
                current_user.instagram = instagram.split("/")[-1]
                instagram = "https://instagram.com/" + instagram.split("/")[-1]
            else:
                instagram = "https://instagram.com/" + instagram
            current_user.instagram_link = instagram
            db.session.commit()
        twitter = request.form.get("twitter")
        if twitter != current_user.twitter:
            current_user.twitter = twitter
            if "/" in twitter:
                current_user.twitter = twitter.split("/")[-1]
                twitter = "https://twitter.com/" + twitter.split("/")[-1]
            else:
                twitter = "https://twitter.com/" + twitter
            current_user.twitter_link = twitter
            db.session.commit()
        facebook = request.form.get("facebook")
        if facebook != current_user.facebook:
            current_user.facebook = facebook
            if "/" in facebook:
                current_user.facebook = facebook.split("/")[-1]
                facebook = "https://facebook.com/" + facebook.split("/")[-1]
            else:
                facebook = "https://facebook.com/" + facebook
            current_user.facebook_link = facebook
            db.session.commit()
        discord = request.form.get("discord")
        if discord != current_user.discord:
            current_user.discord = discord
            if "/" in discord:
                current_user.discord = discord.split("/")[-1]
                discord = "https://discordapp.com/users/" + discord.split("/")[-1]
            else:
                discord = "https://discordapp.com/users/" + discord
            current_user.discord_link = discord
            db.session.commit()
        youtube = request.form.get("youtube")
        if youtube != current_user.youtube:
            current_user.youtube = youtube
            if "/" in youtube:
                current_user.youtube = youtube.split("/")[-1]
                youtube = "https://youtube.com/" + youtube.split("/")[-1]
            else:
                youtube = "https://youtube.com/" + youtube
            current_user.youtube_link = youtube
            db.session.commit()
        github = request.form.get("github")
        if github != current_user.github:
            current_user.github = github
            if "/" in github:
                current_user.github = github.split("/")[-1]
                github = "https://github.com/" + github.split("/")[-1]
            else:
                github = "https://github.com/" + github
            current_user.github_link = github
            db.session.commit()
    
    messageButton = "<a href=\"/profile\"><button class=\"menubtn\" style=\"width:200px\">Exit edit mode</button></a>"
    user = current_user
    description = "<textarea maxlength=\"2500\" rows=\"10\" name=\"description\" placeholder=\"Your description\"></textarea>"
    if user.description is not None:
        description = "<textarea class=\"themeText\" maxlength=\"2500\" rows=\"10\" name=\"description\" placeholder=\"Your description\">"+ str(user.description) +"</textarea>"
    instagram = "<input name=\"instagram\" type=\"text\" placeholder=\"Instagram username\">"
    facebook = "<input name=\"facebook\" type=\"text\" placeholder=\"Facebook username\">"
    youtube = "<input name=\"youtube\" type=\"text\" placeholder=\"Youtube username\">"
    discord = "<input name=\"discord\" type=\"text\" placeholder=\"Discord username\">"
    twitter = "<input name=\"twitter\" type=\"text\" placeholder=\"Twitter username\">"
    github = "<input name=\"github\" type=\"text\" placeholder=\"GitHub username\">"
    if user.instagram_link is not None:
        instagram = "<input name=\"instagram\" type=\"text\" value=\"" + str(user.instagram) + "\">"
    if user.facebook_link is not None:
        facebook = "<input name=\"facebook\" type=\"text\" value=\"" + str(user.facebook) + "\">"
    if user.youtube_link is not None:
        youtube = "<input name=\"youtube\" type=\"text\" value=\"" + str(user.youtube) + "\">"
    if user.discord_link is not None:
        discord = "<input name=\"discord\" type=\"text\" value=\"" + str(user.discord) + "\">"
    if user.twitter_link is not None:
        twitter = "<input name=\"twitter\" type=\"text\" value=\"" + str(user.twitter) + "\">"
    if user.github_link is not None:
        github = "<input name=\"github\" type=\"text\" value=\"" + str(user.github) + "\">"
    other_socials = user.other_socials
    if other_socials is None:
        other_socials = "No other social links"

    allow_adding_byid = ""

    if current_user.can_be_added_by_id is True:
        allow_adding_byid = "<center><p style=\"font-size:32px\"><input type=\"checkbox\" name=\"allow-add\" class=\"checkbox\" style=\"height:42px;width:42px; bottom:-11px;\" checked> Allow people to add you to their servers</p></center>"
    else:
        allow_adding_byid = "<center><p style=\"font-size:32px\"><input type=\"checkbox\" name=\"allow-add\" class=\"checkbox\" style=\"height:42px;width:42px; bottom:-11px;\"> Allow people to add you to their servers</p></center>"

    allow_new_dms = ""
    if current_user.can_be_direct_messaged is True:
        allow_new_dms = "<center><p style=\"font-size:32px\"><input type=\"checkbox\" name=\"allow-dm\" class=\"checkbox\" style=\"height:42px;width:42px; bottom:-11px;\" checked> Allow people to DM you</p></center>"
    else:
        allow_new_dms = "<center><p style=\"font-size:32px\"><input type=\"checkbox\" name=\"allow-dm\" class=\"checkbox\" style=\"height:42px;width:42px; bottom:-11px;\"> Allow people to DM you</p></center>"

    options = allow_adding_byid + allow_new_dms

    savebtn = "<button type=\"submit\" class=\"menubtn\" form=\"profile-data\">Save</button>"
    
    return render_template("profile.html",name=user.name, messagebtn=messageButton, description=description, instagram=instagram, twitter=twitter, facebook=facebook, youtube=youtube, discord=discord, github=github, savebtn=savebtn, options=options)


@socketio.on("connect")
def connect(auth):
    server_id = session.get("server")
    name = session.get("name")
    channel_id = session.get("channel")
    if not server or not name or not channel_id:
        print("exit1")
        return

    server_id = int(server_id)
    channel_id = int(channel_id)
    current_server = Server.query.filter_by(id=server_id).first()
    current_channel = Channel.query.filter_by(id=channel_id).first()
    if current_server is None or current_channel is None:
        leave_room(channel_id)
        print("exit2")
        flash("The server you are trying to access does not exist!", category='Error')
        return redirect(url_for("views.home"))
    
    if verifyUserAccess(server_id) is False:
        disconnect()
    else:
        join_room(channel_id)
    #send({"name" : name.split(" ")[0], "message": " has joined the server"}, to=channel_id)
    #print(f"{name} joined room {channel_id}")

@socketio.on("disconnect")
def disconnect():
    server_id = session.get("server")
    name = session.get("name")

    if not server or not name:
        print("exit1")
        return

    server_id = int(server_id)
    current_server = Server.query.filter_by(id=server_id).first()
    
    leave_room(server_id)

    #send({"name": name.split(" ")[0], "message": "has left the room"}, to=server_id)
    #print(f"{name} has left room {server_id}")

@socketio.on("message")
def message(data):
    server_id = session.get("server")
    name = session.get("name")
    channel_id = int(session.get("channel"))
    
    if not server or not name:
            print("exit1")
            return

    server_id = int(server_id)
    current_server = Server.query.filter_by(id=server_id).first()
    if current_server is None:
        leave_room(channel_id)
        print("exit2")
        flash("The server you are trying to access does not exist!", category='Error')
        return redirect(url_for("views.home"))
    
    if verifyUserAccess(server_id) is False:
        leave_room(channel_id)
        flash("You do not have permission to message this server!", category='Error')
        return redirect(url_for("views.home"))
    else:
        content = {
            "name" : name.split(" ")[0],
            "message" : data["data"],
        }

        channel = Channel.query.filter_by(id=channel_id).first()
        if channel.isLiveChannel is False:
            message = Message(text=data["data"], user_id=current_user.user_id, channel_id=channel_id)
            db.session.add(message)
            db.session.commit()

        print(content)
        send(content, to=channel_id)

@views.route("/set")
@views.route("/set/<theme>")
def set_theme(theme="light"):
  res = make_response(redirect(request.referrer))
  res.set_cookie("theme", theme)
  return res