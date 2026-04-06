import .storage.db as db

class ActivitiesResource:
    def get(self) -> list[dict]:
        activities = db.get_activities()
        # Here you can add any additional processing or filtering if needed
        return activities
    
    def get_completed(self) -> list[dict]:
        return db.get_completed_activities()

    def get_upcoming(self) -> list[dict]:
        return db.get_upcoming_activities()
    
    def get_by_id(self, activity_id: int) -> dict:
        return ActivityResource(activity_id).get()

    def get_by_user_id(self, user_id: int) -> list[dict]:
        return db.get_activities_by_user_id(user_id)
    
    def create_activity(self, activity_data: dict):
        return db.create_activity(activity_data)

class ActivityResource:
    def __init__(self, activity_id):
        self.activity_id = activity_id

    def get(self):
        return db.get_activity_by_id(self.activity_id)

    def update(self, activity_data: dict):
        return db.update_activity(self.activity_id, activity_data)
    
    def delete(self, activity_id: int):
        return db.delete_activity(activity_id)