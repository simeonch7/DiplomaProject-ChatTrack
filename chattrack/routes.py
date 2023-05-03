from flask import render_template, url_for, flash, redirect
from chattrack import app
from chattrack.forms import Registration, Login
from chattrack.models import User, Chat

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
    if form.validate_on_submit():
        flash(f'Hello, {form.username.data} - Account created!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        if form.email.data == "admin@chattrack.com" and form.password.data == "password":
            flash('You are in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful!', 'danger')

    return render_template('login.html', title='Login', form=form)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title="Home", template="Home", chats=dummyChats)

@app.route("/about")
def about():
    return render_template('about.html', title="About", template="About")
