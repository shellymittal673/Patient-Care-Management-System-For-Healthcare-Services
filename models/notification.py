from datetime import datetime
from models import db


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=True)

    notif_type = db.Column(db.String(30))        # Appointment Reminder / Lab Report / Prescription Ready / Billing Reminder / General
    message = db.Column(db.String(255), nullable=False)
    delivery_method = db.Column(db.String(20), default="In-App")   # In-App / SMS / Email

    status = db.Column(db.Enum("Delivered", "Read", "Failed", name="notification_status"),
                        default="Delivered")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship("Patient", backref="notifications", lazy=True)

    def __repr__(self):
        return f"<Notification {self.notif_type} -> P{self.patient_id}>"
