from flask import Blueprint, render_template, request, session
from flask_login import login_required, current_user
from app.resources.activities import ActivitiesResource
from app.utils.formatting_util import enrich_for_cards

from email.message import EmailMessage
import smtplib
import os
import time

bp = Blueprint('landing', __name__)
submitted_emails = {} 

@bp.route('/')
def index():
  return render_template('landing.html')

@bp.route('/about', methods=["GET"])
def about():
    return render_template('about.html')

@bp.route('/legal', methods=["GET"])
def legal():
    return render_template('legal.html')

@bp.route('/contact', methods=["GET", "POST"])
def contact():
    if request.method == "POST":

        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        now = time.time()

        last_submit = session.get("last_contact_submit")
        if last_submit and now - last_submit < 86400:
            return render_template(
                "contact.html",
                error="You have already sent a message today. Please try again tomorrow."
            )
        
        if email in submitted_emails:
            if now - submitted_emails[email] < 86400:
                return render_template(
                    "contact.html",
                    error="This email has already sent a message today."
                )

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

            session["last_contact_submit"] = now 
            submitted_emails[email] = now

            return render_template("contact.html", success=True)

        except Exception as e:
            return render_template("contact.html", error=str(e))

    return render_template("contact.html")

@bp.route('/features', methods=["GET"])
def features():
    return render_template('features.html')

@bp.route('/home', methods=["GET"])
@login_required
def homepage():
    activities_resource = ActivitiesResource()
    upcoming_activities = activities_resource.get_upcoming()
    return render_template('home.html', activities=enrich_for_cards(upcoming_activities))


