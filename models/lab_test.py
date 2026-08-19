from datetime import date, datetime
from models import db


class LabTest(db.Model):
    __tablename__ = "lab_tests"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)

    test_type = db.Column(db.String(120), nullable=False)
    request_date = db.Column(db.Date, default=date.today)
    status = db.Column(db.Enum("Pending", "In Progress", "Completed", name="lab_status"),
                        default="Pending")

    result_summary = db.Column(db.String(255))
    report_filename = db.Column(db.String(255))
    remarks = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    doctor = db.relationship("Doctor", backref="lab_tests", lazy=True)

    def __repr__(self):
        return f"<LabTest {self.test_type} (P{self.patient_id})>"
