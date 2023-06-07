import secrets
import os
import json
import string
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from chattrack import app, db, bcrypt
from chattrack.forms import Registration, Login, UpdateAccount, ChatForm
from chattrack.models import User, Chat
from flask_login import login_user, current_user, logout_user, login_required
import re
import nltk
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def save_picture(form_picture):
    random_name = secrets.token_hex(5)
    extension = os.path.splitext(form_picture.filename)[1]
    picture_filename = random_name + extension
    picture_path = os.path.join(app.root_path, 'static/profile_pictures', picture_filename)

    size = (100, 100)
    thumbnail = Image.open(form_picture)
    thumbnail.thumbnail(size)
    thumbnail.save(picture_path)

    return picture_filename # to write to db

def find_similarities(content, phrases_file_path):
    nltk.download('punkt')
    
    with open(phrases_file_path, 'r') as f:
        initial_phrases = f.readlines()

    content = re.sub(r'[^a-zA-Z0-9\s]', '', content) # Clean up text
    content = content.translate(str.maketrans('', '', string.punctuation))
    content = content.lower()

    def train_bribe_ai(phrases):
        data = []
        vectorizer = TfidfVectorizer()
        tfidf_matrix = None

        data.extend(phrases)
        tfidf_matrix = vectorizer.fit_transform(data)

        def get_related_phrases(chat, threshold=0.3):
            tokens = word_tokenize(chat.lower())
            print("TOKENS:::")
            print(tokens)
            query_vectors = vectorizer.transform([' '.join(tokens)])
            similarity_scores = cosine_similarity(tfidf_matrix, query_vectors).flatten()
            related_indices = similarity_scores.argsort()[::-1]
            related_phrases = []
            for index in related_indices:
                if similarity_scores[index] > threshold:
                    related_phrases.append(data[index])
            return related_phrases

        return get_related_phrases  #returns the get_related_phrases function as a closure. By returning the inner function, 
                                    #we can encapsulate the trained data and vectorizer within the returned function
                                    #allowing us to use them for subsequent calls to get_related_phrases

    get_related_phrases = train_bribe_ai(initial_phrases) # initialization of the function itself
    related_phrases = get_related_phrases(content)        # utilization of the function^
    return related_phrases

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
        flash(f'Здравейте, {form.username.data} - успешно създадохте акаунт!', 'success')
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
            flash('Грешен имейл или парола!', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/chat/new", methods=['GET', 'POST'])
@login_required
def upload_chat():
    form = ChatForm()
    contents = ""
    if form.validate_on_submit():
        contents = str(form.content.data.read().decode('utf-8'))
        suspicious_phrases = find_similarities(contents, 'chattrack/models/inappropriate_behaviour.txt')
        if suspicious_phrases:
            check_for_alert = True
        else:
            check_for_alert = False
        serialized_suspicious_phrases=json.dumps(suspicious_phrases)
        chat = Chat(channel=form.channel.data, content=contents, owner=current_user, 
                    similar_phrases_found=serialized_suspicious_phrases, has_alerts=check_for_alert)
        print("Suspicious Phrases:")
        print(suspicious_phrases)
        db.session.add(chat)
        db.session.commit()
        flash('Успешно качен файл!', 'success')
        return redirect(url_for('home'))
    return render_template('upload_chat.html', title="Upload Chat",legend="Добавете нов файл за сканиране", form=form)

@app.route("/chat/<int:chat_id>", methods=['GET', 'POST'])
@login_required
def chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    deserialized_similar_phrases_found = json.loads(chat.similar_phrases_found)
    return render_template('chat.html', title=chat.channel, chat=chat, phrases_found=deserialized_similar_phrases_found)

@app.route("/chat/<int:chat_id>/update", methods=['GET', 'POST'])
@login_required
def update_chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    if chat.owner != current_user:
        abort(403)
    form = ChatForm()
    if form.validate_on_submit():
        contents = str(form.content.data.read().decode('utf-8'))
        suspicious_phrases = find_similarities(contents, 'chattrack/models/inappropriate_behaviour.txt')
        if suspicious_phrases:
            check_for_alert = True
        else:
            check_for_alert = False
        serialized_suspicious_phrases=json.dumps(suspicious_phrases)
        print("Suspicious Phrases:")
        print(suspicious_phrases)
        chat.channel = form.channel.data
        chat.content = contents
        chat.has_alerts = check_for_alert
        chat.similar_phrases_found = serialized_suspicious_phrases
        db.session.commit()
        flash('Успешно обновен чат!', 'success')
        return redirect(url_for('chat', chat_id = chat.id))
    elif request.method == 'GET':
        form.channel.data = chat.channel
    return render_template('upload_chat.html', title="Update post", legend="Обновете съществуващ чат", form=form)

@app.route("/chat/<int:chat_id>/delete", methods=['POST'])
@login_required
def delete_chat(chat_id):
    chat = Chat.query.get_or_404(chat_id)
    if chat.owner != current_user:
        abort(403)
    db.session.delete(chat)
    db.session.commit()
    flash('Успешно изтрит чат!', 'success')
    return redirect(url_for('home'))

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
        flash('Успешно обновихте акаунта си!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pictures/' + current_user.profile_pic)
    return render_template('account.html', title="account", image_file = image_file, form = form)

@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    queried_chats = Chat.query.order_by(Chat.date_uploaded.desc()).paginate(page=page, per_page=3)
    all_users = User.query.all()
    return render_template('home.html', title="Home", chats=queried_chats, users=all_users)

@app.route("/about")
def about():
    return render_template('about.html', title="About")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/user/<string:username>")
def user_chats(username):
    page = request.args.get('page', 1, type=int)
    all_users = User.query.all()
    user = User.query.filter_by(username=username).first_or_404()
    queried_chats = Chat.query.filter_by(owner=user).order_by(Chat.date_uploaded.desc()).paginate(page=page, per_page=3)
    return render_template('user_chats.html', title="Home", chats=queried_chats, user=user, users=all_users)

@app.route("/alerted/<string:alerted>")
def alerted_chats(alerted):
    if alerted == 'true':
        has_alerts = True
    elif alerted == 'false':
        has_alerts = False
    page = request.args.get('page', 1, type=int)
    all_users = User.query.all()
    queried_chats = Chat.query.filter_by(has_alerts=has_alerts).order_by(Chat.date_uploaded.desc()).paginate(page=page, per_page=3)
    return render_template('alerted_chats.html', title="Home", chats=queried_chats, users=all_users, alerted=alerted)