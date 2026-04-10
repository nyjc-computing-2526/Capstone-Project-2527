from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.resources.users import UsersResource
from app.models.user import User

bp = Blueprint('auth', __name__, url_prefix='/auth')
users_resource = UsersResource()

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            user_data = UsersResource().authenticate(email, password)
            user = User(user_data['id'], user_data['name'], user_data['email'])
            login_user(user) 
            return redirect(url_for('activities.activities'))
        except ValueError as e:
            flash(str(e), "error")
            return render_template('login.html')

    return render_template('login.html')