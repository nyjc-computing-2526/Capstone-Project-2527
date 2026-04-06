from flask import Blueprint, render_template, request
from .resources.activities import ActivitiesResource, ActivityResource

bp = Blueprint('activities', __name__, url_prefix='/activities')
activities_resource = ActivitiesResource()
activity_resource = ActivityResource()

@bp.route('/')
def activities():
    """list all acitivities"""
    completed_activities = activities_resource.get_completed()
    upcoming_activities = activities_resource.get_upcoming()
    total_activities = [completed_activities, upcoming_activities]
    
    return render_template('activities.html', data=total_activities)

@bp.route('/create', methods = ['POST', 'GET'])
def create_activities():
    """create news activities"""
    if request.method == 'POST':
        title = request.form['title']
        description  = request.form['description']
        started_at  = request.form['started_at']
        ended_at  = request.form['ended_at']
 
        activities_resource.create_activity(title, description, started_at, ended_at)

    return render_template('create.html')

@bp.route('/create/<id>')
def view_acitivity():
    """shows details of one specific activity based on id"""
    activity_details = activities_resource.get_activity()

    return render_template('view_acitivity.html', data=activity_details)
