from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.resources.activities import ActivitiesResource
from email.message import EmailMessage
import smtplib
import os

bp = Blueprint('landing', __name__)

@bp.route('/')
def index():
  return render_template('landing.html')

@bp.route('/about', methods=["GET"])
def about():
    return render_template('about.html')

@bp.route('/privacy-policy', methods=["GET"])
def privacy_policy():
    return render_template('legal.html')

@bp.route('/contact', methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        msg = EmailMessage()
        msg["Subject"] = f"New Contact Form Message from {name}"
        msg["From"] = os.environ.get("MAIL_USERNAME")
        msg["To"] = "receiver@example.com"   # change to the actual email you want to receive messages at

        msg.set_content(
            f"""
                You received a new message from your website contact form.

                Name: {name}
                Email: {email}

                Message:
                {message}
            """
        )
        
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(
                    os.environ.get("MAIL_USERNAME"),
                    os.environ.get("MAIL_PASSWORD")
                )
                smtp.send_message(msg)

            return render_template("contact.html", success=True)

        except Exception as e:
            return render_template("contact.html", error=str(e))

    return render_template("contact.html")

@bp.route('/features', methods=["GET"])
def features():
    return render_template('features.html')

@bp.route('/homepage', methods=["GET"])
@login_required
def homepage():
    user_id = current_user.id
    activities_resource = ActivitiesResource()
    upcoming_activities = activities_resource.get_upcoming(user_id)
    return render_template('home.html', activities=upcoming_activities)



