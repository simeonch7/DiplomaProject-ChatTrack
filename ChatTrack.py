from flask import Flask, render_template, url_for

app = Flask(__name__)

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

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', template="Home", chats=dummyChats)

@app.route("/about")
def about():
    return render_template('about.html', template="About")

if __name__ == '__main__':
    app.run(debug=True) # So changes get effect without restarting the app