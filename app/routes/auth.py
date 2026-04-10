from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

import secrets
import resend
import os

from app.resources.users import UsersResource
from app.models.user import User

bp = Blueprint('auth', __name__, url_prefix='/auth')
users_resource = UsersResource()

load_dotenv()
resend.api_key = os.getenv("RESEND_API_KEY")

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """allows user to log in"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            user_data = users_resource.authenticate(email, password)
            user = User(user_data['id'], user_data['name'], user_data['email'])
            login_user(user) 
            return redirect(url_for('activities.activities'))
        except ValueError as e:
            flash(str(e), "error")
            return render_template('login.html')

    return render_template('login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """registers user"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        user_class = request.form['class']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template('register.html')

        user_data = {'email': email, 'password': password, 'name': name, 'class': user_class}
        
        try:
            users_resource.register(user_data)
            flash("Account registered successfully", "success")
            return redirect(url_for('auth.login'))
        except ValueError as e:
            flash(str(e), "error")
            return render_template('register.html')

    return render_template('register.html')
    
@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", "success")
    return redirect(url_for('auth.login'))


@bp.route('/update/<int:id>', methods=['GET', 'POST'])  
@login_required
def update_user(id):
    """updates user details"""
    user_resource = users_resource.user(id)

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        user_class = request.form['class']
        confirm_password = request.form['confirm_password']

        user_data = {}

        if email and email.strip():
            user_data['email'] = email.strip()

        if name and name.strip():
            user_data['name'] = name.strip()

        if user_class and user_class.strip():
            user_data['class'] = user_class.strip()

        if password:
            if password != confirm_password:
                flash("Passwords do not match", "error")
                return render_template('updateuser.html')
            user_data['password'] = password

        if not user_data:
            flash("No valid fields provided for update", "error")
            return render_template('updateuser.html')

        try: 
            user_resource.update(user_data)
            flash("Profile updated successfully", "success")
            return redirect(url_for('activities.activities'))
        except ValueError as e:
            flash(str(e), "error")
            return render_template('updateuser.html')

    return render_template('updateuser.html')

@bp.route('/delete/<int:id>', methods=['POST'])  
@login_required
def delete_user(id):
    """deletes a user"""
    user_resource = users_resource.user(id)

    try: 
        user_resource.delete()
        flash("Profile deleted successfully", "success")
        return redirect(url_for('landing.landing'))
    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for('activities.activities'))
    
@bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "GET":
        return render_template("forgotpassword.html")

    email = request.form.get("email")

    user = users_resource.get_user_by_email(email)

    if user:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

        try:
            users_resource.user(user["id"]).create_verification_token(token, expires_at)
                
            resend.Emails.send({
            "from": email,
            "to": email,
            "subject": "Password Reset",
            "html": f"<p>Click the link to reset your password: <a href='{request.host_url}reset-password?token={token}'>Reset Password</a></p>"
            })
            
            print(f"{request.host_url}/reset-password?token={token}")
        except Exception as e:
            flash(str(e), "error")
            print("Error creating token:", e)
            return redirect("/forgot-password")

    flash("If that email exists, a reset link has been sent.")
    return redirect("/login")


@bp.route("/reset-password")
def reset_password():
    token = request.args.get("token")

    reset = users_resource.verify_token(token)

    if not reset:
        return "Invalid token"

    if reset["expires_at"] < datetime.now(timezone.utc):
        return "Token expired"

    return render_template("resetpassword.html", token=token)


@bp.route("/reset-password", methods=["POST"])
def reset_password_post():
    token = request.form.get("token")
    new_password = request.form.get("password")

    reset = users_resource.verify_token(token)
    user_id = reset["user_id"]

    if not reset:
        return "Invalid token"

    if reset["expires_at"] < datetime.now(timezone.utc):
        return "Token expired"


    users_resource.user(user_id).update({"password": new_password})
    flash("Password reset successfully", "success")
    return redirect("/login")