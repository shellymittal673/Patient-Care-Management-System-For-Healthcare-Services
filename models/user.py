from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models import db


class User(db.Model, UserMixin):
    """
    Central login table. Every person who can log in (Admin, Doctor,
    Nurse, or Patient) has one row here. The `role` column decides
    which dashboard they land on after login.
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone_number = db.Column(db.String(20))
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("admin", "doctor", "nurse", "patient", "pharmacist", name="user_role"),
                      nullable=False, default="patient")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Optional links — populated once the related profile is created
    patient_profile = db.relationship("Patient", backref="user", uselist=False)
    doctor_profile = db.relationship("Doctor", backref="user", uselist=False)

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
