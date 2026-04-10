from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.resources.activities import ActivitiesResource

bp = Blueprint('activities', __name__, url_prefix='/activities')
activities_resource = ActivitiesResource()

@bp.route('/')
def activities():
    """list all activities"""
    total_activities = activities_resource.get_all()
    return render_template('allactivities.html', data=total_activities)

@bp.route('/create', methods = ['POST', 'GET'])
@login_required
def create_activities():
    """create new activities"""
    if request.method == 'POST':
        title = request.form['title']
        description  = request.form['description']
        start_date  = request.form['start_date']
        end_date  = request.form['end_date']
        venue = request.form['venue']
        created_by = current_user.id
    
        activity_data = {'title': title,
                        'description': description,
                        'start_date': start_date,
                        'end_date': end_date,
                        'venue': venue,
                        'created_by': created_by}
        
        activity_id = activities_resource.create_activity(activity_data)

        return redirect(url_for('activities.view_activity', id=activity_id))

    return render_template('createactivity.html')

@bp.route('/<int:id>')
def view_activity(id):
    """shows details of one specific activity based on id"""
    activity_resource = activities_resource.activity(id)
    activity_data = activity_resource.get()
    
    return render_template('view_activity.html', data=activity_data)  

@bp.route('/join/<int:id>', methods=['POST'])
@login_required
def join_activity(id):
    """allows user to join acitivity with that id and redirects them to /activities"""
    user_id = current_user.id
    activity_resource = activities_resource.activity(id)
    success = activity_resource.join(user_id)

    if success:
        return redirect(url_for('activities.activities'))
    else:
        # ill assume that if they somehow cannot join is because they alr inside so bring them back to view activity detail
        return redirect(url_for('activities.view_activity', id=id))
    
@bp.route('/update/<int:id>', methods=['GET', 'POST'])  
@login_required
def update_activity(id):
    activity_resource = activities_resource.activity(id)
    activity_data = activity_resource.get()

    if activity_data is None:
        flash("Activity not found.", "error")
        return redirect(url_for('activities.activities'))

    if activity_data['created_by'] != current_user.id:
        flash("You can only edit your own activities.", "error")
        return redirect(url_for('activities.view_activity', id=id))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        venue = request.form['venue']

        updated_activity_data = {
            'title': title,
            'description': description,
            'start_date': start_date,
            'end_date': end_date,
            'venue': venue
        }

        success = activity_resource.update(updated_activity_data)
        if success:
            return redirect(url_for('activities.view_activity', id=id))
        else:
            flash("Update failed, please try again.", "error")
            return render_template('update_activity.html', data=activity_data)
    else:
        return render_template('update_activity.html', data=activity_data)