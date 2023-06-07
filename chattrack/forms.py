from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from chattrack.models import User

class Login(FlaskForm):
    email = StringField('Имейл', validators=[DataRequired(), Email()])
    password = PasswordField('Парола', validators=[DataRequired()])
    remember_me = BooleanField('Запомни ме')
    submit_field = SubmitField('Вход')

class Registration(FlaskForm):
    email = StringField('Имейл', validators=[DataRequired(), Email()])
    username = StringField('Потребителско име', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Парола', validators=[DataRequired()])
    password_confirmation = PasswordField('Потвърждение на парола', validators=[DataRequired(), EqualTo('password')])
    submit_field = SubmitField('Регистрирайте се')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Потребителското име вече е заето.")
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Имейлът, който се опитвате да използвате, вече е зает.")
        
class UpdateAccount(FlaskForm):
    email = StringField('Имейл', validators=[DataRequired(), Email()])
    username = StringField('Потребителско име', validators=[DataRequired(), Length(min=4, max=20)])
    picture = FileField('Променете профилната си снимка', validators=[FileAllowed(['jpg', 'png'])])
    submit_field = SubmitField('Обнояване на акаунта')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("Потребителското име вече е заето.")
        
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("Имейлът, който се опитвате да използвате, вече е зает.")
            
class ChatForm(FlaskForm):
    channel = StringField('Канал', validators=[DataRequired()])
    content = FileField('Прикачете файл', validators=[FileRequired(), FileAllowed(['txt'])])
    submit_field = SubmitField('Прикачете файл')