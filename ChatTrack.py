from flask import Flask

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    return "<h1>ChatTrack is ready for work!</h1>"

@app.route("/about")
def about():
    return "<p>ChatTrack is a SaaS that lets you monitor communications channels!</p>"

if __name__ == '__main__':
    app.run(debug=True) # So changes get effect without restarting the app