from flask import Blueprint, render_template

bp = Blueprint('landing', __name__)
@bp.route('/')
def index():
  return render_template('landing.html')

@bp.route('/legal')
def legal():
  return render_template('legal.html')
