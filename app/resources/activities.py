import .storage.db as db
from dateutil import parser
from datetime import timezone

class ActivitiesResource:
    def get(self) -> list[dict]:
        return db.get_activities()
    
    def get_completed(self) -> list[dict]:
        return db.get_completed_activities()

    def get_upcoming(self) -> list[dict]:
        return db.get_upcoming_activities()
    
    def get_by_id(self, activity_id: int) -> dict:
        return ActivityResource(activity_id).get()

    def get_by_user_id(self, user_id: int) -> list[dict]:
        if not isinstance(user_id, int):
            user_id = int(user_id)
        return db.get_activities_by_user_id(user_id)
    
    def create_activity(self, activity_data: dict) -> int:
        started_at = parser.parse(activity_data['started_at']).astimezone(timezone.utc)
        if started_at.tzinfo is None:
            started_at = started_at.replace(tzinfo=timezone.utc)
        activity_data['started_at'] = started_at.isoformat()

        ended_at = parser.parse(activity_data['ended_at']).astimezone(timezone.utc)
        if ended_at.tzinfo is None:
            ended_at = ended_at.replace(tzinfo=timezone.utc)
        activity_data['ended_at'] = ended_at.isoformat()

        return db.create_activity(activity_data)

    def delete_activity(self, activity_id: int) -> bool:
        return ActivityResource(activity_id).delete()

class ActivityResource:
    def __init__(self, activity_id):
        self.activity_id = int(activity_id)

    def get(self):
        return db.get_activity_by_id(self.activity_id)

    def update(self, activity_data: dict) -> bool:
        for key, value in activity_data.items():
            if value is None:
                del activity_data[key]

        return db.update_activity(self.activity_id, activity_data)
    
    def delete(self) -> bool:
        return db.delete_activity(self.activity_id)