from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

import app.storage.db as storage_db
from app.resources.activities import ActivitiesResource
from .activity_display import enrich_for_cards, merge_by_id, schedule_for_detail

bp = Blueprint('activities', __name__, url_prefix='/activities')
activities_resource = ActivitiesResource()


def _load_all_activities():
    try:
        return activities_resource.get_all()
    except ValueError:
        flash("Could not load activities.", "error")
        return []


def _load_my_activities(user_id):
    try:
        owned = activities_resource.get_owned(user_id)
        joined = activities_resource.get_joined(user_id)
    except ValueError:
        flash("Could not load your activities.", "error")
        return []
    return merge_by_id(owned, joined)


@bp.route('/')
def activities():
    """list all activities"""
    rows = _load_all_activities()
    return render_template('allactivities.html', data=enrich_for_cards(rows))


@bp.route('/myactivities')
@bp.route('/personal')
@login_required
def my_activities():
    """list all activities created by user and all activities joined by user"""
    combined = _load_my_activities(current_user.id)
    return render_template(
        'myactivities.html',
        activities=enrich_for_cards(combined),
    )

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
    try:
        activity_resource = activities_resource.activity(id)
        activity_data = activity_resource.get()
    except ValueError:
        flash("Activity not found.", "error")
        return redirect(url_for('activities.activities'))

    organizer_email = None
    creator_id = activity_data.get('created_by')
    if creator_id is not None:
        try:
            user_row = storage_db.get_user_by_id(int(creator_id))
            if user_row:
                organizer_email = user_row.get('email')
        except (TypeError, ValueError, Exception):
            organizer_email = None

    return render_template(
        'view_activity.html',
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
        return redirect(url_for('activities.view_activity', id=id))
    
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