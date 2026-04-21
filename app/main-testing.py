"""
Static UI server: same URL map and url_for endpoints as create_app() (main.py),
without blueprints. Run from repo root: python app/main-testing.py
"""

from __future__ import annotations

import importlib.util
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

_APP_DIR = Path(__file__).resolve().parent

_fmt_spec = importlib.util.spec_from_file_location(
    "formatting_util", _APP_DIR / "utils" / "formatting_util.py"
)
_formatting = importlib.util.module_from_spec(_fmt_spec)
assert _fmt_spec.loader is not None
_fmt_spec.loader.exec_module(_formatting)
enrich_for_cards = _formatting.enrich_for_cards
schedule_for_detail = _formatting.schedule_for_detail

app = Flask(
    __name__,
    template_folder=str(_APP_DIR / "templates"),
    static_folder=str(_APP_DIR / "static"),
)
app.secret_key = "main-testing-secret"

# Static UI server has no Flask-Login; templates still reference current_user.
_DEMO_USER_ID = 1


class _MockCurrentUser:
    is_authenticated = True
    id = _DEMO_USER_ID
    name = "Demo User"
    email = "demo@example.com"
    user_class = "Demo Class"


_mock_current_user = _MockCurrentUser()


@app.context_processor
def _inject_current_user():
    return {"current_user": _mock_current_user}


def _parse_dt_utc(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        s = str(value).replace("Z", "+00:00")
        dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _activity_status(activity: dict) -> str:
    """Match activities.activity_details status logic (see app/routes/activities.py)."""
    now = datetime.now(timezone.utc)
    started_at = activity.get("started_at")
    ended_at = activity.get("ended_at")
    if not started_at or not ended_at:
        return "upcoming"
    start = _parse_dt_utc(started_at)
    end = _parse_dt_utc(ended_at)
    if now < start:
        return "upcoming"
    if start <= now <= end:
        return "ongoing"
    return "completed"


_DEMO_PARTICIPANTS_BY_ACTIVITY: dict[int, list[dict]] = {
    1: [
        {
            "id": 1,
            "name": "Demo Organizer",
            "attendance_status": "present",
            "attendance_reason": "",
        },
        {
            "id": 2,
            "name": "Ariana Lim",
            "attendance_status": "late",
            "attendance_reason": "",
        },
        {
            "id": 3,
            "name": "Kai Tan",
            "attendance_status": "excused",
            "attendance_reason": "Medical appointment",
        },
        {
            "id": 4,
            "name": "Noah Ong",
            "attendance_status": "pending",
            "attendance_reason": "",
        },
    ],
    2: [
        {
            "id": 1,
            "name": "Demo Organizer",
            "attendance_status": "present",
            "attendance_reason": "",
        },
        {
            "id": 5,
            "name": "Serene Goh",
            "attendance_status": "absent",
            "attendance_reason": "",
        },
    ],
    3: [
        {
            "id": 7,
            "name": "Mia Santos",
            "attendance_status": "present",
            "attendance_reason": "",
        },
        {
            "id": 1,
            "name": "Demo User",
            "attendance_status": "present",
            "attendance_reason": "",
        },
        {
            "id": 8,
            "name": "Jordan Lee",
            "attendance_status": "late",
            "attendance_reason": "",
        },
    ],
    4: [
        {
            "id": 9,
            "name": "Priya Nair",
            "attendance_status": "present",
            "attendance_reason": "",
        },
        {
            "id": 10,
            "name": "Ethan Cruz",
            "attendance_status": "pending",
            "attendance_reason": "",
        },
        {
            "id": 1,
            "name": "Demo User",
            "attendance_status": "excused",
            "attendance_reason": "Class conflict",
        },
    ],
}

# Lets you open /auth/reset-password with no ?token= for UI inspection; form POST still works.
_DUMMY_RESET_TOKEN = "main-testing-ui-token"

# Demo rows shaped like DB activity dicts (see ActivitiesResource / templates)
_DEMO_ACTIVITIES: list[dict] = [
    {
        "id": 1,
        "title": "Workshop A",
        "started_at": "2026-07-06T10:00:00",
        "ended_at": "2026-07-06T12:00:00",
        "venue": "Room 101",
        "description": "Sample activity for layout testing.",
        "created_by": 1,
    },
    {
        "id": 2,
        "title": "Team sync",
        "started_at": "2026-07-07T14:30:00",
        "ended_at": None,
        "venue": "Online",
        "description": "",
        "created_by": 1,
    },
    {
        "id": 3,
        "title": "Campus Cleanup Drive",
        "started_at": "2026-07-08T08:30:00",
        "ended_at": "2026-07-08T10:30:00",
        "venue": "North Field",
        "description": "Participant-view test case. Demo user joined this activity but is not the organizer.",
        "created_by": 7,
    },
    {
        "id": 4,
        "title": "Robotics Lab Briefing",
        "started_at": "2026-07-09T16:00:00",
        "ended_at": "2026-07-09T17:15:00",
        "venue": "Innovation Hub",
        "description": "Another participant-only activity so the detail page can be checked without organizer tabs.",
        "created_by": 9,
    },
]


def _activity_by_id(activity_id: int) -> dict | None:
    for row in _DEMO_ACTIVITIES:
        if row.get("id") == activity_id:
            return dict(row)
    return None


def _participants_for_activity(activity_id: int) -> list[dict]:
    participants = _DEMO_PARTICIPANTS_BY_ACTIVITY.get(activity_id, [])
    return participants


def _joined_activities() -> list[dict]:
    return [
        dict(activity)
        for activity in _DEMO_ACTIVITIES
        if any(
            participant.get("id") == _DEMO_USER_ID
            for participant in _participants_for_activity(activity["id"])
        )
    ]


def _owned_activities() -> list[dict]:
    return [
        dict(activity)
        for activity in _DEMO_ACTIVITIES
        if activity.get("created_by") == _DEMO_USER_ID
    ]


# --- landing (no prefix; mirrors app/routes/landing.py) ---


@app.route("/", endpoint="landing.index")
def landing_index():
    return render_template("landing.html")


@app.route("/about", methods=["GET"], endpoint="landing.about")
def landing_about():
    return render_template("about.html")


@app.route("/privacy-policy", methods=["GET"], endpoint="landing.privacy_policy")
def landing_privacy_policy():
    return render_template("legal.html")


@app.route("/contact", methods=["GET", "POST"], endpoint="landing.contact")
def landing_contact():
    if request.method == "POST":
        return render_template("contact.html", success=True)
    return render_template("contact.html")


@app.route("/features", methods=["GET"], endpoint="landing.features")
def landing_features():
    return render_template("features.html")


@app.route("/homepage", methods=["GET"], endpoint="landing.homepage")
def landing_homepage():
    return render_template("home.html", activities=enrich_for_cards(_DEMO_ACTIVITIES))


# --- auth (prefix /auth; mirrors app/routes/auth.py paths) ---


@app.route("/auth/login", methods=["GET", "POST"], endpoint="auth.login")
def auth_login():
    if request.method == "POST":
        return redirect(url_for("activities.activities"))
    return render_template("login.html")


@app.route("/auth/register", methods=["GET", "POST"], endpoint="auth.register")
def auth_register():
    if request.method == "POST":
        flash("Account registered successfully", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html")


@app.route("/auth/logout", methods=["GET", "POST"], endpoint="auth.logout")
def auth_logout():
    flash("Logged out successfully", "success")
    return redirect(url_for("auth.login"))


@app.route("/auth/forgot-password", methods=["GET", "POST"], endpoint="auth.forgot_password")
def auth_forgot_password():
    if request.method == "POST":
        flash("If that email exists, a reset link has been sent.", "info")
        return redirect(url_for("auth.login"))
    return render_template("forgotpassword.html")


@app.route("/auth/reset-password", methods=["GET", "POST"], endpoint="auth.reset_password")
def auth_reset_password():
    token = (
        request.args.get("token")
        if request.method == "GET"
        else request.form.get("token")
    )
    if not token:
        token = _DUMMY_RESET_TOKEN
    if request.method == "POST":
        flash("Password reset successfully", "success")
        return redirect(url_for("auth.login"))
    return render_template("resetpassword.html", token=token)


@app.route("/auth/update", methods=["GET", "POST"], endpoint="auth.update_user")
def auth_update_user():
    if request.method == "POST":
        flash("Profile updated successfully", "success")
        return redirect(url_for("activities.activities"))
    return render_template("editprofile.html")


@app.route("/auth/delete/<int:id>", methods=["POST"], endpoint="auth.delete_user")
def auth_delete_user(id: int):
    flash("Profile deleted successfully", "success")
    return redirect(url_for("landing.index"))


@app.route("/auth/verify-password", methods=["POST"], endpoint="auth.verify_password")
def auth_verify_password():
    """Stub for edit-profile modal; always accepts in static UI server."""
    return jsonify({"valid": True})


@app.route("/auth/view/<int:id>", endpoint="auth.view_profile")
def auth_view_profile(id: int):
    user_data = {
        "id": id,
        "name": _mock_current_user.name,
        "email": _mock_current_user.email,
    }
    return render_template(
        "profile.html",
        user_data=user_data,
        activity_data=enrich_for_cards(list(_DEMO_ACTIVITIES)),
    )


@app.route("/auth/view")
def auth_view_redirect():
    return redirect(url_for("auth.view_profile", id=_DEMO_USER_ID))


# --- activities (prefix /activities; mirrors app/routes/activities.py) ---


@app.route(
    "/activities",
    methods=["GET"],
    strict_slashes=False,
    endpoint="activities.activities",
)
def activities_list():
    cards = enrich_for_cards(list(_DEMO_ACTIVITIES))
    return render_template(
        "allactivities.html",
        upcoming=cards,
        ongoing=[],
        completed=[],
    )


@app.route("/activities/myactivities", methods=["GET"], endpoint="activities.my_activities")
def activities_my_activities():
    joined_cards = enrich_for_cards(_joined_activities())
    owned_cards = enrich_for_cards(_owned_activities())
    return render_template(
        "myactivities.html",
        joined=joined_cards,
        owned=owned_cards,
    )


@app.route("/activities/create", methods=["GET", "POST"], endpoint="activities.create_activities")
def activities_create():
    if request.method == "POST":
        return redirect(url_for("activities.activity_details", id=_DEMO_ACTIVITIES[0]["id"]))
    return render_template("createactivity.html")


@app.route("/activities/join/<int:id>", methods=["POST"], endpoint="activities.join_activity")
def activities_join(id: int):
    return redirect(url_for("activities.activities"))


@app.route("/activities/leave/<int:id>", methods=["POST"], endpoint="activities.leave_activity")
def activities_leave(id: int):
    return redirect(url_for("activities.activity_details", id=id))


@app.route("/activities/update/<int:id>", methods=["GET", "POST"], endpoint="activities.update_activity")
def activities_update(id: int):
    row = _activity_by_id(id)
    if not row:
        flash("Activity not found.", "error")
        return redirect(url_for("activities.activities"))
    if request.method == "POST":
        flash("Update saved (main-testing stub).", "success")
        return redirect(url_for("activities.update_activity", id=id))
    return render_template("updateactivity.html", data=row)


@app.route(
    "/activities/attendance/<int:id>",
    methods=["GET", "POST"],
    endpoint="activities.activities_attendance",
)
def activities_attendance(id: int):
    row = _activity_by_id(id)
    if not row:
        flash("Activity not found.", "error")
        return redirect(url_for("activities.activities"))

    if row.get("created_by") != _DEMO_USER_ID:
        flash("Only the organizer can manage attendance.", "error")
        return redirect(url_for("activities.activity_details", id=id))

    participants = _participants_for_activity(id)

    if request.method == "POST":
        for participant in participants:
            participant_id = participant["id"]
            status = request.form.get(f"status_{participant_id}", "pending")
            reason = request.form.get(f"reason_{participant_id}", "").strip()

            participant["attendance_status"] = status
            participant["attendance_reason"] = reason if status == "excused" else ""

        flash("Attendance saved (main-testing stub).", "success")
        return redirect(url_for("activities.activities_attendance", id=id))

    return render_template(
        "activityattendance.html",
        data=row,
        participants=participants,
    )


@app.route("/activities/delete/<int:id>", methods=["POST"], endpoint="activities.delete_activity")
def activities_delete(id: int):
    return redirect(url_for("activities.activities"))


@app.route("/activities/<int:id>", methods=["GET"], endpoint="activities.activity_details")
def activities_activity_details(id: int):
    row = _activity_by_id(id)
    if not row:
        flash("Activity not found.", "error")
        return redirect(url_for("activities.activities"))
    return render_template(
        "activitydetails.html",
        data=row,
        schedule=schedule_for_detail(row),
        organizer_email="organizer@example.com",
        participants=_participants_for_activity(id),
        status=_activity_status(row),
    )


# --- convenience paths used by templates / older links (not blueprint names) ---


@app.route("/home", methods=["GET"])
def home():
    return redirect(url_for("landing.homepage"))


@app.route("/allactivities", methods=["GET"])
def allactivities_alias():
    return redirect(url_for("activities.activities"))


@app.route("/myactivities", methods=["GET"])
def myactivities_alias():
    return redirect(url_for("activities.my_activities"))


@app.route("/create", methods=["GET", "POST"])
def create_alias():
    return redirect(url_for("activities.create_activities"))


@app.route("/activity", methods=["GET"])
def activity_card_demo():
    return render_template("activitycard.html")


@app.route("/legal", methods=["GET"], endpoint="landing.legal")
def landing_legal():
    """Same URL and endpoint as app/routes/landing.py `legal` (footer link)."""
    return render_template("legal.html")


@app.route("/login", methods=["GET"])
def login_alias():
    return redirect(url_for("auth.login"))


@app.route("/register", methods=["GET"])
def register_alias():
    return redirect(url_for("auth.register"))


@app.route("/forgetpassword", methods=["GET", "POST"])
def forgotpassword_alias():
    return redirect(url_for("auth.forgot_password"))


@app.route("/reset", methods=["GET", "POST"])
def resetpassword_alias():
    q = request.query_string.decode() if request.query_string else ""
    target = url_for("auth.reset_password")
    if q:
        target = f"{target}?{q}"
    return redirect(target)


if __name__ == "__main__":
    app.run(debug=True)
