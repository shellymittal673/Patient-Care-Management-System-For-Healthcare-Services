from datetime import date
from models import db


class Allergy(db.Model):
    __tablename__ = "allergies"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)

    allergen = db.Column(db.String(120), nullable=False)
    reaction = db.Column(db.String(255))
    added_on = db.Column(db.Date, default=date.today)

    def __repr__(self):
        return f"<Allergy {self.allergen} (P{self.patient_id})>"
