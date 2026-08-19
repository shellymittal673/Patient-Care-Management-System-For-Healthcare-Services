from datetime import date, datetime
from models import db


class Consultation(db.Model):
    """
    A single doctor visit record. This doubles as the patient's
    'Diagnosis History' entry shown on the EHR page (Milestone 2 Day 1)
    and the record created by the Consultation Management form (Day 2) -
    the same table drives both, which is how the two connect.
    """
    __tablename__ = "consultations"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)

    consultation_date = db.Column(db.Date, default=date.today)
    symptoms = db.Column(db.Text)
    diagnosis = db.Column(db.String(255))
    treatment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    doctor = db.relationship("Doctor", backref="consultations", lazy=True)
    prescriptions = db.relationship("Prescription", backref="consultation", lazy=True)

    def __repr__(self):
        return f"<Consultation P{self.patient_id} on {self.consultation_date}>"
