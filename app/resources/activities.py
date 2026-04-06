import .storage.db as db

class ActivitiesResource:
    def get(self):
        activities = db.get_activities()
        # Here you can add any additional processing or filtering if needed
        return activities
    
    def get_completed(self):
        return db.get_completed_activities()

    def get_upcoming(self):
        return db.get_upcoming_activities()
    
    def get_by_id(self, activity_id):
        return ActivityResource(activity_id).get()
    
    def create_activity(self, activity_data):
        return db.create_activity(activity_data)

class ActivityResource:
    def __init__(self, activity_id):
        self.activity_id = activity_id

    def get(self):
        return db.get_activity_by_id(self.activity_id)

    def update(self, activity_data):
        return db.update_activity(self.activity_id, activity_data)
    
    def delete(self, activity_id):
        return db.delete_activity(activity_id)