
from database import db


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    hashed_password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    authenticated = True

    def __init__(self, email, hashed_password=None, is_admin=False):
        self.email = email
        self.hashed_password = hashed_password
        self.is_admin = is_admin

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'hashed_password': self.hashed_password,
            'is_admin': self.is_admin
        }

    def is_active(self):
        return True

    def get_id(self):
        return self.email

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False
