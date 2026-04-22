from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import secrets
import resend
import os
from app.resources.users import UsersResource
from app.resources.activities import ActivitiesResource
from app.models.user import User
from app.utils.recaptcha import verify_recaptcha
from ..utils.formatting_util import enrich_for_cards, merge_by_id, schedule_for_detail

bp = Blueprint('auth', __name__, url_prefix='/auth')
users_resource = UsersResource()
activities_resource = ActivitiesResource()

load_dotenv()
resend.api_key = os.getenv("RESEND_API_KEY")

def validate_password(password):
    """verifies that password is between 8 to 24 characters inclusive,
    include at least 1 special character, uppercase letter, lowercase letter and number"""
    errors = []
    if not (8 <= len(password) <= 24):
        errors.append("Password must be between 8 and 24 characters long")
    
    special = any(not char.isalnum() for char in password)
    upper = any(char.isupper() for char in password)
    lower = any(char.islower() for char in password)
    number = any(char.isdigit() for char in password)
    
    if not special:
        errors.append("Password must include at least one special character")
    if not upper:
        errors.append("Password must include at least one uppercase letter")
    if not lower:
        errors.append("Password must include at least one lowercase letter")
    if not number:
        errors.append("Password must include at least one number")
    
    if errors:
        raise ValueError("\n".join(errors))
    return True


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """allows user to log in"""
    if request.method == 'POST':
        form_data = {"email": request.form.get('email', '').strip()}
        recaptcha_token = request.form.get('g-recaptcha-response')
        
        if not recaptcha_token or not verify_recaptcha(recaptcha_token):
            flash("Please complete the captcha.", "error")
            return render_template('login.html', **form_data)

        email = form_data['email']
        password = request.form['password'].strip()
        if not email or not password:
            flash("Please enter your email and password.", "error")
            return render_template('login.html', **form_data)
        
        try:
            user_data = users_resource.authenticate_with_lockout(email, password)

            if not user_data.get("verified"):
                flash("Please verify your email before logging in.", "error")
                return render_template('login.html', **form_data)

            users_resource.reset_login_lockout(user_data['id'])
            user_obj = User(user_data['id'], user_data['name'], user_data['email'], user_data['user_class'], None)
            login_user(user_obj) 
            return redirect(url_for('landing.homepage'))
        
        except ValueError as e:
            flash(str(e), "error")
            return render_template('login.html', **form_data)

    return render_template('login.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """registers user"""
    if request.method == 'POST':
        form_data = {
            "email": request.form['email'],
            "name": request.form['name'],
            "user_class": request.form['class'],
        }
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not all([form_data['email'].strip(), form_data['name'].strip(), form_data['user_class'].strip(), password.strip(), confirm_password.strip()]):
            flash("All fields are required.", "error")
            return render_template('register.html', **form_data)

        recaptcha_token = request.form.get('g-recaptcha-response')
        if not recaptcha_token or not verify_recaptcha(recaptcha_token):
            flash("Please complete the captcha.", "error")
            print("Error completeting captcha")
            return render_template('register.html', **form_data)

        try:
            validate_password(password)
        except ValueError as e:
            flash(str(e), "error")
            return render_template('register.html', **form_data) #saves the data except for password so that they dont have to reenter everything and tell front end

        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template('register.html', **form_data)
                
        user_data = {'email': form_data['email'], 'password': password, 'name': form_data['name'], 'user_class': form_data['user_class']}
        
        try:
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now(timezone.utc) + timedelta(days=2)
            
            user_id = users_resource.register(user_data)
            user_resource = users_resource.user(user_id)
            data = {
                "token": token,
                "expiry": expires_at,                
                "type": "verify_email"
            }
            user_resource.create_verification_token(data)
            
            verify_url = f"{request.host_url}auth/verify-email?token={token}"
            resend.Emails.send({
                "from": "Activity Alligator <noreply@activityalligator.com>",
                "to": form_data["email"],
                "template": {
                    "id": "email-verification",
                    "variables": {
                        "link": verify_url
                    }
                }
            })

            flash("Please check your email to verify your account for creation :).", "info")
            return redirect(url_for('auth.register'))

        except Exception as e:
            flash(str(e), "error")
            print(str(e))
            return render_template('register.html', **form_data)
    
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
    
    try:
        id = verify["user_id"]
        user_resource = users_resource.user(id)
        user_resource.update({"verified": True})
        users_resource.invalidate_token(token)

        flash("Email verified successfully! Your account has been created!", "success")
        return redirect(url_for('auth.login'))

    except Exception as e:
        flash(str(e), "error")
        return redirect(url_for('auth.register'))


@bp.route('/verify-password', methods=['POST'])
@login_required
def verify_password():
    password = request.json.get('password')
    try:
        users_resource.authenticate(current_user.email, password)
        return {'valid': True}
    except ValueError:
        return {'valid': False}


@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", "success")
    return redirect(url_for('landing.index'))


@bp.route('/view/<int:id>')  
@login_required
def view_profile(id):
    """allows user to view their profile details"""
    user_resource = users_resource.user(id)
    user_data = user_resource.get()
    activity_data = activities_resource.get_owned(id)
    return render_template('profile.html', user_data=user_data, activity_data=enrich_for_cards(activity_data))


@bp.route('/update', methods=['GET', 'POST'])  
@login_required
def update_user():
    """updates user details"""
    user_resource = users_resource.user(current_user.id)

    if request.method == 'POST':
        form_type = request.form.get('form_type', 'profile')

        if form_type == 'password':
            current_password = request.form.get('current_password').strip()
            password = request.form.get('password').strip()
            confirm_password = request.form.get('confirm_password')

            if not current_password:
                flash("Please verify your current password first.", "error")
                return render_template('editprofile.html')

            try:
                users_resource.authenticate(current_user.email, current_password)
            except ValueError as e:
                flash(str(e), "error")
                return render_template('editprofile.html')

            if not password:
                flash("Please enter a new password.", "error")
                return render_template('editprofile.html')
            
            try:
                validate_password(password)
            except ValueError as e:
                flash(str(e), "error")
                return render_template('editprofile.html')
            
            if password != confirm_password:
                flash("Passwords do not match", "error")
                return render_template('editprofile.html')

            try:
                user_resource.update({'password': password})
                flash("Password updated successfully", "success")
                return redirect(url_for('auth.update_user'))
            except ValueError as e:
                flash(str(e), "error")
                return render_template('editprofile.html')

        email = request.form.get('email')
        name = request.form.get('name')
        user_class = request.form.get('class')

        user_data = {}

        if email and email.strip():
            user_data['email'] = email.strip()

        if name and name.strip():
            user_data['name'] = name.strip()

        if user_class and user_class.strip():
            user_data['user_class'] = user_class.strip()

        if not user_data:
            flash("No valid fields provided for update", "error")
            return render_template('editprofile.html')

        try: 
            user_resource.update(user_data)
            flash("Profile updated successfully", "success")
            return redirect(url_for('auth.view_profile', id=current_user.id))
        except ValueError as e:
            flash(str(e), "error")
            return render_template('editprofile.html')

    return render_template('editprofile.html')


@bp.route('/delete/<int:id>', methods=['POST'])  
@login_required
def delete_user(id):
    """deletes a user"""
    if id != current_user.id:
        flash("You can only delete your own account.", "error")
        return redirect(url_for('auth.view_profile', id=current_user.id))

    user_resource = users_resource.user(id)

    try: 
        user_resource.delete()
        logout_user()
        flash("Profile deleted successfully", "success")
        return redirect(url_for('landing.index'))
    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for('auth.view_profile', id=current_user.id))
    

@bp.route('/forgot-password', methods=['GET', 'POST'])  
def forgot_password():
    if request.method == "GET":
        return render_template("forgotpassword.html")

    email = request.form.get("email").strip()
    if not email:
        flash("Please enter your email.", "error")
        return render_template("forgotpassword.html")
    
    user = users_resource.get_user_by_email(email)

    if user:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        try:
            data = {
                "token": token,
                "expiry": expires_at,
                "type": "forgot_password"
            }
            users_resource.user(user["id"]).create_verification_token(data)
            reset_url = f"{request.host_url}auth/reset-password?token={token}"
            resend.Emails.send({
                "from": "Activity Alligator <noreply@activityalligator.com>",
                "to": form_data["email"],
                "template": {
                    "id": "password-reset",
                    "variables": {
                        "link": verify_url
                    }
                }
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
        password = request.form.get("password").strip()
        confirm_password = request.form.get("confirm_password")

        if not password:
            flash("Please enter a new password.", "error")
            return render_template("resetpassword.html", token=token)
        
        try:
            validate_password(password)
        except ValueError as e:
            flash(str(e), "error")
            return render_template("resetpassword.html", token=token)
    
        if password != confirm_password:
            flash("The passwords you keyed in are not the same. Please check again.", "error")
            return render_template("resetpassword.html", token=token)
        
        try:
            users_resource.user(reset["user_id"]).update({"password": password})
            users_resource.invalidate_token(token)
            flash("Password reset successfully", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(str(e), "error")
            print(str(e))
            return render_template("resetpassword.html", token=token)

    return render_template("resetpassword.html", token=token)
