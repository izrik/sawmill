
from database import db


class Option(db.Model):
    key = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.String(100), nullable=True)

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def to_dict(self):
        return {
            'key': self.key,
            'value': self.value
        }
