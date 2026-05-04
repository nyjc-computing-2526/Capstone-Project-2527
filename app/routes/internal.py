import os

import resend
from dotenv import load_dotenv
from flask import Blueprint, jsonify, request

from app.resources.activities import ActivitiesResource

load_dotenv()

bp = Blueprint('internal', __name__, url_prefix='/internal')
activities_resource = ActivitiesResource()


def _authorized():
    expected_token = os.getenv("REMINDER_CRON_TOKEN")
    supplied_token = request.headers.get("X-Reminder-Token")
    return bool(expected_token) and supplied_token == expected_token


def _format_started_at(value):
    if hasattr(value, "strftime"):
        return value.strftime("%d %b %Y, %I:%M %p")
    return str(value)


def _send_reminder_email(reminder):
    resend.api_key = os.getenv("RESEND_API_KEY")
    if not resend.api_key:
        raise RuntimeError("RESEND_API_KEY environment variable is not set.")

    resend.Emails.send({
        "from": "Activity Alligator <noreply@activityalligator.com>",
        "to": reminder["user_email"],
        "subject": f"Reminder: {reminder['title']} is coming up",
        "html": f"""
            <p>Hi {reminder['user_name']},</p>
            <p>This is a reminder that <strong>{reminder['title']}</strong> is coming up soon.</p>
            <p>
                <strong>When:</strong> {_format_started_at(reminder['started_at'])}<br>
                <strong>Where:</strong> {reminder['venue']}
            </p>
            <p>See you there!</p>
        """
    })


@bp.route('/send-reminders', methods=['POST'])
def send_reminders():
    if not _authorized():
        return jsonify({"error": "Unauthorized"}), 401

    reminders = activities_resource.get_due_reminders(hours_before=24)
    sent = 0
    failed = 0

    for reminder in reminders:
        try:
            _send_reminder_email(reminder)
            if activities_resource.mark_reminder_sent(reminder["activity_id"], reminder["user_id"]):
                sent += 1
        except Exception:
            failed += 1

    return jsonify({
        "checked": len(reminders),
        "sent": sent,
        "failed": failed
    })
