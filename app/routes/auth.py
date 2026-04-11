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

            if not user_data.get("is_verified"):
                flash("Please verify your email before logging in.", "error")
                return render_template('login.html')
            
            user = User(user_data['id'], user_data['name'], user_data['email'], user_data['user_class'], user_data['password'])
            #is passing password like that safe...?
            login_user(user) 
            return redirect(url_for('landing.home'))
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
        
        user_data = {'email': email, 'password': password, 'name': name, 'user_class': user_class}
        
        try:
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
            
            user_id = users_resource.register(user_data)
            #assuming register returns id
            user_resource = users_resource.user(user_id)
            user_resource.create_verification_token(token, expires_at, 'verify_email')
            
            verify_url = f"{request.host_url}auth/verify-email?token={token}"
            resend.Emails.send({
                "from": "onboarding@resend.dev",
                "to": email,
                "subject": "Verify Email",
                "html": f"<p>Click to verify your email: <a href='{verify_url}'>Verify Email</a></p>"
            })
            flash("Please check your email to verify your account for creation :).", "info")
            return render_template('register.html')

        except Exception as e:
            flash(str(e), "error")
            print(str(e))
            return render_template('register.html')


@bp.route('/verify-email')
def verify_email():
    """verifies user email"""        
    token = request.args.get("token")

    if not token:
        return "Missing token", 400

    verify = users_resource.verify_token(token, 'verify_email')

    if not verify:
        return "Invalid token", 400

    if verify["expiry"] < datetime.now(timezone.utc):
        return "Token expired", 400
    
    id = verify["user_id"]
    user_resource = users_resource.user(id)

    try:
        user_resource.update({"is_verified": True})
        users_resource.invalidate_token(token)

        flash("Email verified successfully! Your account has been created!", "success")
        return redirect(url_for('auth.login'))

    except Exception as e:
        flash(str(e), "error")
        return redirect(url_for('auth.register'))


@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", "success")
    return redirect(url_for('auth.login'))


@bp.route('/view/<int:id>')  
@login_required
def view_profile(id):
    """allows user to view their profile details"""
    user_resource = users_resource.user(id)
    user_data = user_resource.get()
    return render_template('view_profile.html', user_data=user_data)


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
            user_data['user_class'] = user_class.strip()

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
            return redirect(url_for('landing.home'))
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
        return redirect(url_for('landing.home'))
    
@bp.route('/forgot-password', methods=['GET', 'POST'])  
def forgot_password():
    if request.method == "GET":
        return render_template("forgotpassword.html")

    email = request.form.get("email")
    user = users_resource.get_user_by_email(email)

    if user:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        try:
            users_resource.user(user["id"]).create_verification_token(token, expires_at, 'forgot_password')
            reset_url = f"{request.host_url}auth/reset-password?token={token}"
            resend.Emails.send({
                "from": "onboarding@resend.dev",
                "to": email,
                "subject": "Password Reset",
                "html": f"<p>Click to reset your password: <a href='{reset_url}'>Reset Password</a></p>"
            })
        except Exception as e:
            flash(str(e), "error")
            print(str(e))
            return redirect(url_for('auth.forgot_password'))

    flash("If that email exists, a reset link has been sent.", "info")
    return redirect(url_for('auth.login'))

@bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    token = request.args.get("token") if request.method == "GET" else request.form.get("token")

    if not token:
        return "Missing token", 400

    reset = users_resource.verify_token(token, 'forgot_password')

    if not reset:
        return "Invalid token", 400

    if reset["expiry"] < datetime.now(timezone.utc):
        return "Token expired", 400

    if request.method == "POST":
        if request.form.get("password") != request.form.get("confirm_password"):
            flash("The passwords you keyed in are not the same. Please check again.", "error")
            return render_template("resetpassword.html", token=token)
        new_password = request.form.get("password")
        try:
            users_resource.user(reset["user_id"]).update({"password": new_password})
            users_resource.invalidate_token(token)
            flash("Password reset successfully", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(str(e), "error")
            print(str(e))
            return render_template("resetpassword.html", token=token)

    return render_template("resetpassword.html", token=token)