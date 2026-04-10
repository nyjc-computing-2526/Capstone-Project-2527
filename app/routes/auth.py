from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.resources.users import UsersResource
from app.models.user import User

bp = Blueprint('auth', __name__, url_prefix='/auth')
users_resource = UsersResource()

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
    
@bp.route('/forgotpassword', methods=['GET', 'POST'])  
def forgot_password():
    """allows a user to reset their password"""
    if request.method == 'POST':
        email = request.form['email']
        
        user = users_resource._get_user_by_email(email)
        if not user:
            flash("No account found with that email.", "error")
            return render_template("forgotpassword.html")
        id = user['id']
        user_resource = users_resource.user(id)

        try: 
            user_resource.forgotpassword(email)
            flash("Password reset successfully", "success")
            return redirect(url_for('auth.login'))
        except ValueError as e:
            flash(str(e), "error")
            render_template("forgotpassword.html")
    
    render_template("forgotpassword.html")
