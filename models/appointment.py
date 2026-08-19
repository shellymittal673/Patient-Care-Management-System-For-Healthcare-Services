from datetime import datetime
from models import db


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)

    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    reason_for_visit = db.Column(db.String(255))
    status = db.Column(
        db.Enum("Scheduled", "Completed", "Cancelled", "No-show", name="appointment_status"),
        default="Scheduled",
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Appointment P{self.patient_id} -> D{self.doctor_id} on {self.appointment_date}>"
