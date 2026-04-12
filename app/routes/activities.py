from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.resources.users import UsersResource
from app.resources.activities import ActivitiesResource
from ..utils.formatting_util import enrich_for_cards, merge_by_id, schedule_for_detail

bp = Blueprint('activities', __name__, url_prefix='/activities')
activities_resource = ActivitiesResource()
users_resource = UsersResource()


@bp.route('/')
@bp.route('')
def activities():
    try:
        rows = activities_resource.get_all()
    except ValueError:
        flash("Could not load activities.", "error")
        rows = []
    return render_template('allactivities.html', data=enrich_for_cards(rows))


@bp.route('/myactivities')
@login_required
def my_activities():
    try:
        owned = activities_resource.get_owned(current_user.id)
        joined = activities_resource.get_joined(current_user.id)
    except ValueError:
        flash("Could not load your activities.", "error")
        owned, joined = [], []
    combined = merge_by_id(owned, joined)
    return render_template('myactivities.html', activities=enrich_for_cards(combined))

@bp.route('/create', methods = ['POST', 'GET'])
@login_required
def create_activities():
    """create new activity"""
    if request.method == 'POST':
        title = request.form['title']
        description  = request.form['description']
        start_date  = request.form['start_date']
        end_date  = request.form['end_date']
        venue = request.form['venue']
        created_by = current_user.id
    
        activity_data = {'title': title,
                        'description': description,
                        'started_at': start_date,
                        'ended_at': end_date,
                        'venue': venue,
                        'created_by': created_by}
        
        activity_id = activities_resource.create_activity(activity_data)

        return redirect(url_for('activities.activity_details', id=activity_id))

    return render_template('createactivity.html')

@bp.route('/<int:id>')
def activity_details(id):
    try:
        activity_data = activities_resource.activity(id).get()
    except ValueError:
        flash("Activity not found.", "error")
        return redirect(url_for('activities.activities'))

    organizer_email = None
    creator_id = activity_data.get('created_by')
    if creator_id:
        try:
            user = users_resource.user(int(creator_id)).get()
            organizer_email = user.get('email')
        except ValueError:
            organizer_email = None

    return render_template(
        'activity_details.html',
        data=activity_data,
        schedule=schedule_for_detail(activity_data),
        organizer_email=organizer_email or '',
    )


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
        return redirect(url_for('activities.activity_details', id=id))
    
@bp.route('/leave/<int:id>', methods=['POST'])
@login_required
def leave_activity(id):
    """allows user to leave acitivity with that id and redirects them to /activities"""
    user_id = current_user.id
    activity_resource = activities_resource.activity(id)
    success = activity_resource.leave(user_id)

    if success:
        return redirect(url_for('activities.activities'))
    else:
        return redirect(url_for('activities.activity_details', id=id))
    
@bp.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_activity(id):
    try:
        activity_resource = activities_resource.activity(id)
        activity_data = activity_resource.get()
    except ValueError:
        flash("Activity not found.", "error")
        return redirect(url_for('activities.activities'))

    if activity_data['created_by'] != current_user.id:
        flash("You can only edit your own activities.", "error")
        return redirect(url_for('activities.activity_details', id=id))

    if request.method == 'POST':
        updated_data = {
            'title': request.form['title'],
            'description': request.form['description'],
            'started_at': request.form['start_date'], 
            'ended_at': request.form['end_date'],       
            'venue': request.form['venue'],
        }
        try:
            activity_resource.update(updated_data)
            return redirect(url_for('activities.activity_details', id=id))
        except ValueError as e:
            flash(str(e), "error")
            return render_template('update_activity.html', data=activity_data)
    else:
        return render_template('update_activity.html', data=activity_data)

@bp.route('/delete/<int:id>', methods=['POST'])
def delete_activity(id):
    try:
        activity_resource = activities_resource.activity(id)
        success = activity_resource.delete()
        
        if not success:
            raise ValueError(f'Deletion of activity {id} not successful')
    
    except Exception as e:
        print(e)
    
    return redirect(url_for('activities.activities'))
    
    
    
