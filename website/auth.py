from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, ServerList, Server, Category, Channel, Message
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import random

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in successfully!", category='Success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash("Incorrect email or password, try again.", category='Error')

    return render_template("login.html", chats="")
@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        if len(email) < 5:
            flash("Email address must be longer than 4 characters.", category='Error')
        elif len(name) < 3:
            flash("Name must be longer than 2 characters.", category='Error')
        elif len(password1) < 7:
            flash("Password must be longer than 7 characters.", category='Error')
        elif password1 != password2:
            flash("Passwords don't match.", category='Error')
        else:
            user = User.query.filter_by(email=email).first()

            if user is not None:
                flash("User with this email address already exists!", category='Error')
            else:
                all_users = User.query.filter_by().all()
                handles = []
                for user in all_users:
                    handles.append(user.handle)
                
                new_handle = random.randint(10000000, 99999999)
                while new_handle in handles:
                    new_handle = random.randint(10000000, 99999999)
                    
                new_user = User(email=email, name=name, handle=new_handle, password=generate_password_hash(password1, 'sha256'))
                db.session.add(new_user)
                db.session.commit()
                flash("Account successfully created!", category='success')
                return redirect(url_for('views.home'))



    return render_template("sign-up.html", chats="")