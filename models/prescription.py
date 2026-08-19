from datetime import date, datetime
from models import db


class Prescription(db.Model):
    __tablename__ = "prescriptions"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    consultation_id = db.Column(db.Integer, db.ForeignKey("consultations.id"), nullable=True)

    prescription_date = db.Column(db.Date, default=date.today)
    diagnosis = db.Column(db.String(255))
    special_instructions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    doctor = db.relationship("Doctor", backref="prescriptions", lazy=True)
    items = db.relationship("PrescriptionItem", backref="prescription", lazy=True,
                             cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Prescription P{self.patient_id} on {self.prescription_date}>"


class PrescriptionItem(db.Model):
    __tablename__ = "prescription_items"

    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey("prescriptions.id"), nullable=False)

    medicine_name = db.Column(db.String(120), nullable=False)
    dosage = db.Column(db.String(50))
    frequency = db.Column(db.String(50))
    duration = db.Column(db.String(50))

    def __repr__(self):
        return f"<PrescriptionItem {self.medicine_name}>"
