from datetime import date, datetime
from models import db


class Feedback(db.Model):
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=True)
    consultation_id = db.Column(db.Integer, db.ForeignKey("consultations.id"), nullable=True)

    rating_doctor = db.Column(db.Integer)       # 1-5
    rating_hospital = db.Column(db.Integer)     # 1-5
    rating_lab = db.Column(db.Integer)          # 1-5
    rating_pharmacy = db.Column(db.Integer)     # 1-5
    comments = db.Column(db.Text)

    feedback_date = db.Column(db.Date, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship("Patient", backref="feedback_entries", lazy=True)
    doctor = db.relationship("Doctor", backref="feedback_entries", lazy=True)
    consultation = db.relationship("Consultation", backref="feedback_entries", lazy=True)

    @property
    def average_rating(self):
        vals = [v for v in [self.rating_doctor, self.rating_hospital,
                             self.rating_lab, self.rating_pharmacy] if v]
        return round(sum(vals) / len(vals), 1) if vals else None

    def __repr__(self):
        return f"<Feedback P{self.patient_id} avg={self.average_rating}>"
