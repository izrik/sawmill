
from database import db


class LogEntry(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True)
    server = db.Column(db.String(100), index=True)
    log_name = db.Column(db.String(1000), index=True)
    message = db.Column(db.Text(), nullable=True)

    def __init__(self, timestamp, server, log_name, message):
        self.timestamp = timestamp
        self.server = server
        self.log_name = log_name
        self.message = message

    def to_dict(self):
        return {
            'timestamp': self.timestamp,
            'server': self.server,
            'log_name': self.log_name,
            'message': self.message,
        }
