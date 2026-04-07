import .storage.db as db
from dateutil import parser
from datetime import timezone

ALLOWED_ACTIVITY_COLUMNS = {'title', 'started_at', 'ended_at', 'description'}

class ActivitiesResource:
    def get(self) -> list[dict]:
        try:
            return db.get_activities()
        except Exception as e:
            # Log the error (e.g., using logging module)
            raise ValueError(f"Failed to retrieve activities: {str(e)}")
    
    def get_completed(self) -> list[dict]:
        try:
            return db.get_completed_activities()
        except Exception as e:
            raise ValueError(f"Failed to retrieve completed activities: {str(e)}")

    def get_upcoming(self) -> list[dict]:
        try:
            return db.get_upcoming_activities()
        except Exception as e:
            raise ValueError(f"Failed to retrieve upcoming activities: {str(e)}")
    
    def get_by_id(self, activity_id: int) -> dict:
        return ActivityResource(activity_id).get()
        
    def get_by_user_id(self, user_id: int) -> list[dict]:
        try:
            if not isinstance(user_id, int):
                user_id = int(user_id)
            if user_id <= 0:
                raise ValueError("Invalid user ID: must be a positive integer")
            return db.get_activities_by_user_id(user_id)
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Failed to retrieve activities for user {user_id}: {str(e)}")
    
    def create_activity(self, activity_data: dict) -> int:
        if not isinstance(activity_data, dict):
            raise ValueError("Activity data must be a dictionary")

        activity_data = dict(activity_data)  # Create a copy to avoid mutating input

        required_fields = ['started_at', 'ended_at', 'title', 'description']
        for field in required_fields:
            if field not in activity_data or not isinstance(activity_data[field], str):
                raise ValueError(f"Missing or invalid {field}: must be a string")
            
        invalid = activity_data.keys() - ALLOWED_ACTIVITY_COLUMNS

        if invalid:
            raise ValueError(f"Invalid column(s): {invalid}")

        try:
            started_at = parser.parse(activity_data['started_at']).astimezone(timezone.utc)
            activity_data['started_at'] = started_at.isoformat()

            ended_at = parser.parse(activity_data['ended_at']).astimezone(timezone.utc)
            activity_data['ended_at'] = ended_at.isoformat()

        except ValueError as e:
            raise ValueError(f"Invalid date format or logic: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to create activity: {str(e)}")
        
        if started_at >= ended_at:
            raise ValueError("Started time must be before ended time") 
        return db.create_activity(activity_data)

    def delete_activity(self, activity_id: int) -> bool:
        return ActivityResource(activity_id).delete()


class ActivityResource:
    def __init__(self, activity_id):
        try:
            self.activity_id = int(activity_id)
            if self.activity_id <= 0:
                raise ValueError("Activity ID must be a positive integer")
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid activity ID: {str(e)}")


    def get(self):
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
        if not isinstance(activity_data, dict):
            raise ValueError("Activity data must be a dictionary")
        
        activity_data = dict(activity_data)  # Create a copy to avoid mutating input

        invalid = activity_data.keys() - ALLOWED_ACTIVITY_COLUMNS
        if invalid:
            raise ValueError(f"Invalid column(s): {invalid}")

        activity_data = {k: v for k, v in activity_data.items() if v}

        if not activity_data:
            raise ValueError("No valid fields to update")
        try:
            success = db.update_activity(self.activity_id, activity_data)
            if not success:
                raise ValueError(f"Activity {self.activity_id} not found or update failed")
            return success
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Failed to update activity {self.activity_id}: {str(e)}")
    
    def delete(self) -> bool:
        try:
            success = db.delete_activity(self.activity_id)
            if not success:
                raise ValueError(f"Activity {self.activity_id} not found or delete failed")
            return success
        except ValueError:
            raise 
        except Exception as e:
            raise ValueError(f"Failed to delete activity {self.activity_id}: {str(e)}")