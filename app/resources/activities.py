import app.storage.db as db
from dateutil import parser
from datetime import timezone

ALLOWED_ACTIVITY_COLUMNS = {'title', 'started_at', 'ended_at', 'description', 'created_by', 'venue'}
ALLOWED_STATUS = {'pending', 'present', 'late', 'excused', 'absent'}

class ActivitiesResource:
    """Resource class for managing activities collection operations."""

    def get_all(self) -> list[dict]:
        """Retrieve all activities.

        Returns:
            list[dict]: A list of all activities.

        Raises:
            ValueError: If retrieval fails.
        """
        try:
            return db.get_activities()
        except Exception as e:
            raise ValueError(f"Failed to retrieve activities: {str(e)}")
    
    def get_completed(self) -> list[dict]:
        """Retrieve all completed activities.

        Returns:
            list[dict]: A list of completed activities.

        Raises:
            ValueError: If retrieval fails.
        """
        try:
            return db.get_completed_activities()
        except Exception as e:
            raise ValueError(f"Failed to retrieve completed activities: {str(e)}")

    def get_upcoming(self) -> list[dict]:
        """Retrieve all upcoming activities.

        Returns:
            list[dict]: A list of upcoming activities.

        Raises:
            ValueError: If retrieval fails.
        """
        try:
            return db.get_upcoming_activities()
        except Exception as e:
            raise ValueError(f"Failed to retrieve upcoming activities: {str(e)}")
        
    def get_ongoing(self) -> list[dict]:
        """Retrieve all ongoing activities.

        Returns:
            list[dict]: A list of ongoing activities.

        Raises:
            ValueError: If retrieval fails.
        """
        try:
            return db.get_ongoing_activities()
        except Exception as e:
            raise ValueError(f"Failed to retrieve ongoing activities: {str(e)}")
    
    def get_owned(self, user_id: int) -> list[dict]:
        """Retrieve activities owned by a specific user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            list[dict]: A list of activities owned by the user.

        Raises:
            ValueError: If user_id is invalid or retrieval fails.
        """
        try:
            if not isinstance(user_id, int):
                user_id = int(user_id)
            if user_id < 0:
                raise ValueError("Invalid user ID: must be a positive integer")
            return db.get_owned(user_id)
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Failed to retrieve owned activities for user {user_id}: {str(e)}")
        
    def get_joined(self, user_id: int) -> list[dict]:
        """Retrieve activities joined by a specific user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            list[dict]: A list of activities joined by the user.

        Raises:
            ValueError: If user_id is invalid or retrieval fails.
        """
        try:
            if not isinstance(user_id, int):
                user_id = int(user_id)
            if user_id < 0:
                raise ValueError("Invalid user ID: must be a positive integer")
            return db.get_joined(user_id)
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Failed to retrieve joined activities for user {user_id}: {str(e)}")
    
    
    def create_activity(self, activity_data: dict) -> int:
        """Create a new activity.

        Args:
            activity_data (dict): Dictionary containing activity details.

        Returns:
            int: The ID of the created activity.

        Raises:
            ValueError: If activity_data is invalid or creation fails.
        """
        if not isinstance(activity_data, dict):
            raise ValueError("Activity data must be a dictionary")

        activity_data = dict(activity_data)

        required_fields = ['started_at', 'ended_at', 'title', 'description', 'created_by', 'venue']
        for field in required_fields:
            if field not in activity_data or not (isinstance(activity_data[field], str) or isinstance(activity_data[field], int)):
                raise ValueError(f"Missing or invalid {field}: must be a string or integer")
            
        invalid = activity_data.keys() - ALLOWED_ACTIVITY_COLUMNS
        if invalid:
            raise ValueError(f"Invalid column(s): {invalid}")

        try:
            started_at = parser.parse(activity_data['started_at']).astimezone(timezone.utc)
            activity_data['started_at'] = started_at.isoformat()

            ended_at = parser.parse(activity_data['ended_at']).astimezone(timezone.utc)
            activity_data['ended_at'] = ended_at.isoformat()

            if started_at >= ended_at:
                raise ValueError("Started time must be before ended time") 

            return db.create_activity(activity_data)
        except ValueError as e:
            raise ValueError(f"Invalid date format or logic: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to create activity: {str(e)}")

    def activity(self, activity_id) -> "ActivityResource":
        """Get an ActivityResource instance for a specific activity.

        Args:
            activity_id: The ID of the activity.

        Returns:
            ActivityResource: An instance of ActivityResource for the activity.
        """
        return ActivityResource(activity_id)

class ActivityResource:
    """Resource class for managing individual activity operations."""

    def __init__(self, activity_id):
        """Initialize ActivityResource with an activity ID.

        Args:
            activity_id: The ID of the activity.

        Raises:
            ValueError: If activity_id is invalid.
        """
        try:
            self.activity_id = int(activity_id)
            if self.activity_id < 0:
                raise ValueError("Activity ID must be a positive integer")
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid activity ID: {str(e)}")

    def get(self) -> dict:
        """Retrieve the activity details.

        Returns:
            dict: The activity data.

        Raises:
            ValueError: If activity not found or retrieval fails.
        """
        try:
            activity = db.get_activity_by_id(self.activity_id)
            if activity is None:
                raise ValueError(f"Activity {self.activity_id} not found")
            return activity
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Failed to retrieve activity {self.activity_id}: {str(e)}")

    def update(self, activity_data: dict) -> bool:
        """Update the activity with new data.

        Args:
            activity_data (dict): Dictionary containing fields to update.

        Returns:
            bool: True if update was successful.

        Raises:
            ValueError: If activity_data is invalid or update fails.
        """
        if not isinstance(activity_data, dict):
            raise ValueError("Activity data must be a dictionary")
        
        activity_data = dict(activity_data)

        invalid = activity_data.keys() - ALLOWED_ACTIVITY_COLUMNS
        if invalid:
            raise ValueError(f"Invalid column(s): {invalid}")

        activity_data = {k: v for k, v in activity_data.items() if v is not None}
        activity_data["id"] = self.activity_id

        if not activity_data:
            raise ValueError("No valid fields to update")
            
        try:
            success = db.update_activity(activity_data)
            if not success:
                raise ValueError(f"Activity {self.activity_id} not found or update failed")
            return success
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Failed to update activity {self.activity_id}: {str(e)}")
    
    def delete(self) -> bool:
        """Delete the activity.

        Returns:
            bool: True if deletion was successful.

        Raises:
            ValueError: If deletion fails.
        """
        try:
            success = db.delete_participant_activity(self.activity_id)
            if not success:
                raise ValueError(f"Activity {self.activity_id} not found or delete failed")
            
            success = db.delete_activity(self.activity_id)
            if not success:
                raise ValueError(f"Activity {self.activity_id} not found in Participant")
            return success
        except ValueError:
            raise 
        except Exception as e:
            raise ValueError(f"Failed to delete activity {self.activity_id}: {str(e)}")
    
    def join(self, user_id: int) -> bool:
        """Allow a user to join the activity.

        Args:
            user_id (int): The ID of the user joining.

        Returns:
            bool: True if join was successful.

        Raises:
            ValueError: If user_id is invalid or join fails.
        """
        try:
            if not isinstance(user_id, int):
                user_id = int(user_id)
            if user_id < 0:
                raise ValueError("Invalid user ID: must be a positive integer")
            
            if db.get_participant(self.activity_id, user_id):
                raise ValueError(f"You have already joined this activity!")
        
            success = db.join_activity(self.activity_id, user_id)
            if not success:
                raise ValueError(f"Activity {self.activity_id} not found or join failed")
            return success
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Failed to join activity {self.activity_id} for user {user_id}: {str(e)}")

    def leave(self, user_id: int) -> bool:
        """Allow a user to leave the activity.

        Args:
            user_id (int): The ID of the user leaving.

        Returns:
            bool: True if leave was successful.

        Raises:
            ValueError: If user_id is invalid or leave fails.
        """
        try:
            if not isinstance(user_id, int):
                user_id = int(user_id)
            if user_id < 0:
                raise ValueError("Invalid user ID: must be a positive integer")
            success = db.leave_activity(self.activity_id, user_id)
            if not success:
                raise ValueError(f"Activity {self.activity_id} not found or leave failed")
            return success
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Failed to leave activity {self.activity_id} for user {user_id}: {str(e)}")

    def get_participants(self) -> list[dict]:
        """Retrieve the participants of the activity.

        Returns:
            list[dict]: A list of participants.

        Raises:
            ValueError: If retrieval fails.
        """
        try:
            return db.get_participants(self.activity_id)
        except Exception as e:
            raise ValueError(f"Failed to retrieve participants for activity {self.activity_id}: {str(e)}")
        

    def update_attendance_for_participant(self, user_id: int, status: str, reason: str | None, marked_by: int) -> bool:
        try:
            if not isinstance(user_id, int):
                user_id = int(user_id)
            if user_id < 0:
                raise ValueError("Invalid user ID: must be a positive integer")

            if not isinstance(marked_by, int):
                marked_by = int(marked_by)
            if marked_by < 0:
                raise ValueError("Invalid marked_by: must be a positive integer")

            if not isinstance(status, str):
                raise ValueError("Invalid status: must be a string")

            status = status.strip().lower()
            if status not in ALLOWED_STATUS:
                raise ValueError(f"Invalid status: {status}")
            
            if reason is not None and not isinstance(reason, str):
                raise ValueError("Invalid reason: must be a string")
            normalized_reason = (reason or "").strip()
            if status == "excused":
                if not normalized_reason:
                    raise ValueError("Reason is required when status is 'excused'")
            else:
                normalized_reason = None

            success = db.update_participant_attendance(self.activity_id, user_id,status, normalized_reason, marked_by)
            if not success:
                raise ValueError(f"Participant {user_id} not found in activity {self.activity_id} or update failed")

            return True

        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Failed to update attendance for user {user_id} in activity {self.activity_id}: {str(e)}")

        
        
