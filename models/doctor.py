from datetime import datetime
from models import db


class Doctor(db.Model):
    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=True)

    full_name = db.Column(db.String(120), nullable=False)
    specialization = db.Column(db.String(100))
    qualification = db.Column(db.String(150))
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(120))
    department = db.Column(db.String(100))          # milestone field
    hospital_branch = db.Column(db.String(120))      # dataset field
    years_experience = db.Column(db.Integer)          # dataset field
    available_time = db.Column(db.String(100))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    appointments = db.relationship("Appointment", backref="doctor", lazy=True,
                                    cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Doctor {self.full_name} ({self.specialization})>"
