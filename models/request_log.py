from datetime import datetime
from models import db


class RequestLog(db.Model):
    """
    Every HTTP request the app serves gets timed and logged here (see the
    before_request/after_request hooks in app.py). This is what powers the
    Performance & Testing dashboard with REAL numbers instead of invented
    ones — average response time, error rate, and per-module breakdown are
    all computed from this table.
    """
    __tablename__ = "request_logs"

    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.String(120))
    blueprint = db.Column(db.String(50))
    method = db.Column(db.String(10))
    status_code = db.Column(db.Integer)
    response_time_ms = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<RequestLog {self.endpoint} {self.status_code} {self.response_time_ms}ms>"
