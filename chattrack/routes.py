import secrets
import os
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from chattrack import app, db, bcrypt
from chattrack.forms import Registration, Login, UpdateAccount
from chattrack.models import User, Chat
from flask_login import login_user, current_user, logout_user, login_required

dummyChats = [
    {
        'author': 'Jane Doe',
        'channel': 'Teams',
        'content': 'Jane: Hey, how are you? Client: Shut up and help me, lazy!',
        'date_posted': 'May 2nd, 2023'
    },
    {
        'author': 'Jane Doe',
        'channel': 'Bloomberg chat',
        'content': 'Jane: Hey, how can I help you? Client: Are you crazy!?',
        'date_posted': 'May 2nd, 2023'
    }
]

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = Registration()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username = form.username.data, email = form.email.data, password = hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Hello, {form.username.data} - Account created!. You are now able to login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = Login()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            if request.args.get('next'):
                return redirect(request.args.get('next'))
            else:    
                return redirect(url_for('home'))
        else:
            flash('Login unsuccessful!', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pictures', picture_filename)

    size = (125, 125)
    thmb = Image.open(form_picture)
    thmb.thumbnail(size)
    thmb.save(picture_path)

    return picture_filename

@app.route("/chat/new", methods=['GET', 'POST'])
@login_required
def new_chat():
    return render_template('upload_chat.html', title="Upload Chat")

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccount()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
        current_user.profile_pic = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pictures/' + current_user.profile_pic)
    return render_template('account.html', title="account", image_file = image_file, form = form)
    
@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title="Home", chats=dummyChats)

@app.route("/about")
def about():
    return render_template('about.html', title="About")
