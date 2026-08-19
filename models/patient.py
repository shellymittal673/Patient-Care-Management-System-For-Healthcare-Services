from datetime import date, datetime
from models import db


class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=True)

    full_name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer)                     # kept for quick display (milestone spec)
    date_of_birth = db.Column(db.Date)               # kept for dataset compatibility
    gender = db.Column(db.String(10))
    contact_number = db.Column(db.String(20))
    email = db.Column(db.String(120))
    aadhaar_number = db.Column(db.String(20))
    address = db.Column(db.String(255))
    blood_group = db.Column(db.String(5))
    medical_history = db.Column(db.Text)

    # ---- EHR Medical Summary (Milestone 2, Day 1) ----
    height_cm = db.Column(db.Float)
    weight_kg = db.Column(db.Float)
    smoking = db.Column(db.String(10))          # Yes / No
    alcohol = db.Column(db.String(20))          # No / Occasional / Regular
    chronic_diseases = db.Column(db.String(255))
    remarks = db.Column(db.String(255))

    registration_date = db.Column(db.Date, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    appointments = db.relationship("Appointment", backref="patient", lazy=True,
                                    cascade="all, delete-orphan")
    medical_records = db.relationship("MedicalRecord", backref="patient", lazy=True,
                                       cascade="all, delete-orphan")
    allergies = db.relationship("Allergy", backref="patient", lazy=True,
                                 cascade="all, delete-orphan", order_by="Allergy.added_on.desc()")
    medications = db.relationship("Medication", backref="patient", lazy=True,
                                   cascade="all, delete-orphan", order_by="Medication.start_date.desc()")
    consultations = db.relationship("Consultation", backref="patient", lazy=True,
                                     cascade="all, delete-orphan",
                                     order_by="Consultation.consultation_date.desc()")
    prescriptions = db.relationship("Prescription", backref="patient", lazy=True,
                                     cascade="all, delete-orphan",
                                     order_by="Prescription.prescription_date.desc()")
    lab_tests = db.relationship("LabTest", backref="patient", lazy=True,
                                 cascade="all, delete-orphan",
                                 order_by="LabTest.request_date.desc()")
    past_illnesses = db.relationship("PastIllness", backref="patient", lazy=True,
                                      cascade="all, delete-orphan")
    past_surgeries = db.relationship("PastSurgery", backref="patient", lazy=True,
                                      cascade="all, delete-orphan")
    family_history = db.relationship("FamilyHistory", backref="patient", lazy=True,
                                      cascade="all, delete-orphan")

    @property
    def bmi(self):
        if self.height_cm and self.weight_kg and self.height_cm > 0:
            h_m = self.height_cm / 100
            return round(self.weight_kg / (h_m * h_m), 1)
        return None

    def __repr__(self):
        return f"<Patient {self.full_name}>"
