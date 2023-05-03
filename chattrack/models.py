from chattrack import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    profile_pic = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    chats = db.relationship('Chat', backref='owner', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.profile_pic}')"

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    has_alerts = db.Column(db.Boolean, nullable=False, default=False)
    date_uploaded = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return f"Chat('{self.has_alerts}', '{self.date_uploaded}')"
