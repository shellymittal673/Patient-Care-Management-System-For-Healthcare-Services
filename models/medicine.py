from datetime import date, datetime
from models import db


class Medicine(db.Model):
    __tablename__ = "medicines"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50))          # Tablet / Capsule / Syrup / ...
    manufacturer = db.Column(db.String(120))
    stock = db.Column(db.Integer, default=0)
    unit_price = db.Column(db.Numeric(10, 2), default=0)
    expiry_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    dispense_records = db.relationship("DispenseRecord", backref="medicine", lazy=True)

    @property
    def status(self):
        if self.expiry_date and self.expiry_date < date.today():
            return "Expired"
        if self.stock is not None and self.stock <= 20:
            return "Low Stock"
        return "Available"

    def __repr__(self):
        return f"<Medicine {self.name}>"


class DispenseRecord(db.Model):
    __tablename__ = "dispense_records"

    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey("prescriptions.id"), nullable=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey("medicines.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    dispensed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    dispensed_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship("Patient", backref="dispense_records", lazy=True)
    prescription = db.relationship("Prescription", backref="dispense_records", lazy=True)

    def __repr__(self):
        return f"<DispenseRecord med={self.medicine_id} qty={self.quantity}>"
