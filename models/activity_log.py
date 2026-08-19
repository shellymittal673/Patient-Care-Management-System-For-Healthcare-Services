from datetime import datetime
from models import db


class ActivityLog(db.Model):
    """
    A real audit trail — every key action in the system (patient registered,
    appointment booked, consultation completed, lab uploaded, prescription
    generated, payment received, appointment cancelled, user login) writes
    one row here. Powers 'Recent System Activity' on the dashboard and the
    Audit Logs page (Milestone 4).
    """
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50), nullable=False)   # e.g. "Patient Registered"
    description = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    icon = db.Column(db.String(20), default="info")      # used to pick an icon client-side
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="activity_logs", lazy=True)

    def __repr__(self):
        return f"<ActivityLog {self.action}>"


def log_activity(action, description, user_id=None, icon="info"):
    """Call this from any route right after a meaningful write succeeds."""
    entry = ActivityLog(action=action, description=description, user_id=user_id, icon=icon)
    db.session.add(entry)
    # Intentionally NOT committing here — caller's own db.session.commit()
    # (right after the real action) will include this row atomically.
