from flask import *

app = Flask(__name__)

@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/allactivities")
def allactivities():
    return render_template("allactivities.html")

@app.route("/myactivities")
def myactivities():
    return render_template("myactivities.html")

app.run()
