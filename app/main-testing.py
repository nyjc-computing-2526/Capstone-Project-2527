from flask import *

app = Flask(__name__)


def _stub_page(title: str) -> str:
    """Minimal page for routes linked from the landing nav; templates may be added later."""
    css_href = url_for("static", filename="styles.css")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"/><title>{title}</title>
<link rel="stylesheet" href="{css_href}"/></head>
<body><main style="padding:2rem"><h1>{title}</h1><p><a href="/">Back to home</a></p></main></body></html>"""


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/legal")
def legal():
    return render_template("legal.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/auth/login")
def auth_login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/auth/register")
def auth_register():
    return render_template("register.html")


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/auth/view")
def auth_view():
    return render_template("profile.html")


@app.route("/activities")
def activities_index():
    return render_template("allactivities.html")


@app.route("/activities/personal")
def activities_personal():
    return render_template("myactivities.html")


@app.route("/activities/create", methods=["GET", "POST"])
def activities_create():
    return render_template("createactivity.html")


@app.route("/allactivities")
def allactivities():
    return render_template("allactivities.html")


@app.route("/myactivities")
def myactivities():
    return render_template("myactivities.html")


@app.route("/activity")
def activitycard():
    return render_template("activitycard.html")


@app.route("/forgetpassword", methods=["GET", "POST"])
def forgotpassword():
    return render_template("forgotpassword.html")


@app.route("/reset", methods=["GET", "POST"])
def resetpassword():
    return render_template("resetpassword.html")


@app.route("/create", methods=["GET", "POST"])
def create():
    return render_template("createactivity.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/features")
def features():
    return render_template("features.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


app.run()
