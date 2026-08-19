from models import db


class PastIllness(db.Model):
    __tablename__ = "past_illnesses"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    illness = db.Column(db.String(120), nullable=False)
    year = db.Column(db.String(10))

    def __repr__(self):
        return f"<PastIllness {self.illness} (P{self.patient_id})>"


class PastSurgery(db.Model):
    __tablename__ = "past_surgeries"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    surgery = db.Column(db.String(120), nullable=False)
    surgery_date = db.Column(db.Date)

    def __repr__(self):
        return f"<PastSurgery {self.surgery} (P{self.patient_id})>"


class FamilyHistory(db.Model):
    __tablename__ = "family_history"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    condition = db.Column(db.String(120), nullable=False)
    relation = db.Column(db.String(50))

    def __repr__(self):
        return f"<FamilyHistory {self.condition} (P{self.patient_id})>"
