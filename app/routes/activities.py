from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.resources.users import UsersResource
from app.resources.activities import ActivitiesResource
from ..utils.formatting_util import enrich_for_cards, merge_by_id, schedule_for_detail
from ..utils.sanitize_util import sanitize_input

bp = Blueprint('activities', __name__, url_prefix='/activities')
activities_resource = ActivitiesResource()
users_resource = UsersResource()


@bp.route('/')
@bp.route('')
def activities():
    """shows all activities"""
    search_query = request.args.get("query")
    if search_query: 
        search_query = search_query.lower()
    try:
        upcoming = activities_resource.get_upcoming()
        completed = activities_resource.get_completed()
        ongoing = activities_resource.get_ongoing()
        
        if search_query:
            upcoming = list(filter(lambda row: row['title'].lower().startswith(search_query), upcoming))
            completed = list(filter(lambda row: row['title'].lower().startswith(search_query), completed))
            ongoing = list(filter(lambda row: row['title'].lower().startswith(search_query), ongoing))
            
    except ValueError:
        flash("Could not load activities.", "error")
        upcoming, completed, ongoing = [], [], []
    return render_template('allactivities.html', 
        upcoming=enrich_for_cards(upcoming), 
        completed=enrich_for_cards(completed),
        ongoing=enrich_for_cards(ongoing),
        search_query=search_query
    )


@bp.route('/myactivities')
@login_required
def my_activities():
    """shows user's activities"""
    try:
        owned = activities_resource.get_owned(current_user.id)
        joined = activities_resource.get_joined(current_user.id)
    except ValueError:
        flash("Could not load your activities.", "error")
        owned, joined = [], []
    return render_template('myactivities.html',
        owned=enrich_for_cards(owned),
        joined=enrich_for_cards(joined)
    )

@bp.route('/create', methods = ['POST', 'GET'])
@login_required
def create_activities():
    """creates new activity"""
    if request.method == 'POST':
        try:
            if len(activities_resource.get_owned(current_user.id)) >= 5:
                flash ("You have reached the maximum number of activities you can create (5).", "error")
                return render_template('createactivity.html')
            title = sanitize_input(request.form['title'])
            description  = sanitize_input(request.form['description'])
            start_date  = request.form['start_date']
            end_date  = request.form['end_date']
            venue = sanitize_input(request.form['venue'])
            created_by = current_user.id
        
            activity_data = {
                'title': title,
                'description': description,
                'started_at': start_date,
                'ended_at': end_date,
                'venue': venue,
                'created_by': created_by
            } 
            
            activity_id = activities_resource.create_activity(activity_data)

            return redirect(url_for('activities.activity_details', id=activity_id))
        except Exception:
            flash("Failed to create activity. Please try again.", "error")
            return render_template("createactivity.html")

    return render_template('createactivity.html')

@bp.route('/<int:id>')
def activity_details(id):
    """shows details of activity with that id"""
    try:
        activity_data = activities_resource.activity(id).get()
        participants = activities_resource.activity(id).get_participants()
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

    # determine status
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    started_at = activity_data.get('started_at')
    ended_at = activity_data.get('ended_at')

    if started_at and ended_at:
        if now < started_at:
            status = 'upcoming'
        elif started_at <= now <= ended_at:
            status = 'ongoing'
        else:
            status = 'completed'
    else:
        status = 'upcoming'

    return render_template(
        'activitydetails.html',
        data=activity_data,
        schedule=schedule_for_detail(activity_data),
        organizer_email=organizer_email or '',
        participants=participants or [],
        status=status
    )


@bp.route('/join/<int:id>', methods=['POST'])
@login_required
def join_activity(id):
    """allows user to join acitivity with that id and redirects them to activty details of that id"""
    user_id = current_user.id

    try:
        activity_resource = activities_resource.activity(id)
    except ValueError:
        flash("Activity not found.", "error")
        return redirect(url_for('activities.activities'))
    
    try:
        activity_resource.join(user_id)
        flash("Successfully joined activity.", "success")
    except ValueError:
        flash("Unable to join activity. Please try again.", "error")
        
    return redirect(url_for('activities.activity_details', id=id)) #changed to just redirect to activity_details no matter success or not
    
@bp.route('/leave/<int:id>', methods=['POST'])
@login_required
def leave_activity(id):
    """allows user to leave acitivity with that id and redirects them to /activities"""
    user_id = current_user.id

    try:
        activity_resource = activities_resource.activity(id)
    except ValueError:
        flash("Activity not found.", "error")
        return redirect(url_for('activities.activities'))
    
    try:
        activity_resource.leave(user_id)
        flash("Successfully left activity.", "success")
        return redirect(url_for('activities.my_activities'))
    except ValueError:
        flash("Unable to leave activity. Please try again.", "error")
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
        try:
            updated_data = {
                'title': sanitize_input(request.form['title']),
                'description': sanitize_input(request.form['description']),
                'started_at': request.form['start_date'],
                'ended_at': request.form['end_date'],
                'venue': sanitize_input(request.form['venue']),
            }
            activity_resource.update(updated_data)
            return redirect(url_for('activities.activity_details', id=id))
        except Exception:
            flash("Failed to update activity. Please try again later.", "error")
            return render_template('updateactivity.html', data=activity_data)
    else:
        return render_template('updateactivity.html', data=activity_data)


@bp.route('/delete/<int:id>', methods=['POST']) #cleaned up the code
@login_required
def delete_activity(id):
    try:
        activity_resource = activities_resource.activity(id)
        activity_data = activity_resource.get()
    except ValueError:
        flash("Activity not found.", "error")
        return redirect(url_for('activities.activities'))
    
    try:
        if activity_data['created_by'] != current_user.id:
            flash("You can only delete your own activities.", "error")
            return redirect(url_for('activities.activity_details', id=id))

        activity_resource.delete()
        flash("Activity deleted successfully", "success")
        return redirect(url_for('activities.my_activities'))
    
    except ValueError:
        flash("Failed to delete activity. Please try again.", "error")
        return redirect(url_for('activities.activity_details', id=id))
    
    
@bp.route('/attendance/<int:id>')
@login_required
def activities_attendance(id):
    """view attendance for the activity with that id"""
    try:
        activity_resource = activities_resource.activity(id)
        activity_data = activity_resource.get()
    except ValueError:
        flash("Activity not found.", "error")
        return redirect(url_for('activities.activities'))
    
    try:
        if activity_data['created_by'] != current_user.id:
            flash("Only the organsier can view the attendance.", "error")
            return redirect(url_for('activities.activity_details', id=id))
    
        participants = activity_resource.get_participants()
        return render_template(
            'activityattendance.html',
            data=activity_data,
            participants=participants
        )
    
    except ValueError:
        flash("Failed to retrieve participants.", "error")
        return redirect(url_for('activities.activity_details', id=id))
        
    
@bp.route('/attendance/<int:id>', methods=['POST'])
@login_required
def update_attendance(id):
    """allows organiser to update attendance for activity with that id and redirects them to attendance page"""
    try:
        activity_resource = activities_resource.activity(id)
        activity_data = activity_resource.get()
    except ValueError:
        flash("Activity not found.", "error")
        return redirect(url_for('activities.activities'))
    
    try:
        if activity_data['created_by'] != current_user.id:
            flash("Only the organsier can update the attendance.", "error")
            return redirect(url_for('activities.activity_details', id=id))
        
        participants = activity_resource.get_participants()    
    
    except ValueError:  
        flash("Failed to load participants.", "error")  
        return redirect(url_for('activities.activity_details', id=id))  
 
    try:
        failed_updates = []
        for participant in participants:
            participant_id = participant['id']
            participant_name = participant['name'] #easier to see which updates failed if using their name

            status = request.form.get(f'status_{participant_id}', 'pending')
            reason = request.form.get(f'reason_{participant_id}', '')
            marked_by = current_user.id

            try:
                activity_resource.update_attendance_for_participant(participant_id, status, reason, marked_by)
            except ValueError:
                failed_updates.append(participant_name)

        if failed_updates:
            flash(f"Attendance update failed for: " + ", ".join(failed_updates),"error")
        else:
            flash("Attendance updated successfully.", "success")
    
    except ValueError:
        flash("Failed to update attendance.", "error")
    
    return redirect(url_for('activities.activities_attendance', id=id))
