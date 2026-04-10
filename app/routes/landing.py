from flask import Blueprint, render_template, request

bp = Blueprint('landing', __name__)
@bp.route('/')
def index():
  return render_template('landing.html')

@bp.route('/about', methods=["GET"])
def about():
  if request.method == "GET":
    return render_template('about.html')

@bp.route('/contact', methods=["GET","POST"])
def contact():
  if request.method == "GET":
    return render_template('contact.html')
  else:
    if request.method == "POST":
      pass


@bp.route('/features', methods=["GET"])
def features():
  if request.method == "GET":
    return render_template('features.html')




