from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, name, email, user_class, password):
        self.id = id
        self.name = name
        self.email = email
        self.user_class = user_class
        self.password = password