from flask import Flask, render_template, url_for, flash, redirect
from forms import Registration, Login

app = Flask(__name__)
app.config['SECRET_KEY'] = '89417394d6e0fb06109c676235a8b00b'

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
    return render_template('login.html', title='Login', form=form)

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', template="Home", chats=dummyChats)

@app.route("/about")
def about():
    return render_template('about.html', template="About")

if __name__ == '__main__':
    app.run(debug=True) # So changes get effect without restarting the app