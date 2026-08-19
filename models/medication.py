from datetime import date
from models import db


class Medication(db.Model):
    __tablename__ = "medications"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)

    medicine_name = db.Column(db.String(120), nullable=False)
    dosage = db.Column(db.String(50))
    frequency = db.Column(db.String(50))
    start_date = db.Column(db.Date, default=date.today)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<Medication {self.medicine_name} (P{self.patient_id})>"
