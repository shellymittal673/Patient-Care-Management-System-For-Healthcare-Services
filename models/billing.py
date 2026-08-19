from datetime import date, datetime
from models import db


class Bill(db.Model):
    __tablename__ = "bills"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)

    bill_date = db.Column(db.Date, default=date.today)
    sub_total = db.Column(db.Numeric(10, 2), default=0)
    discount = db.Column(db.Numeric(10, 2), default=0)
    tax = db.Column(db.Numeric(10, 2), default=0)
    total_amount = db.Column(db.Numeric(10, 2), default=0)

    payment_method = db.Column(db.String(30))          # Cash / UPI / Card / Insurance
    payment_status = db.Column(db.Enum("Paid", "Unpaid", "Pending", name="payment_status_enum"),
                                default="Pending")
    transaction_id = db.Column(db.String(80))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship("Patient", backref="bills", lazy=True)
    items = db.relationship("BillItem", backref="bill", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Bill #{self.id} P{self.patient_id} {self.total_amount}>"


class BillItem(db.Model):
    __tablename__ = "bill_items"

    id = db.Column(db.Integer, primary_key=True)
    bill_id = db.Column(db.Integer, db.ForeignKey("bills.id"), nullable=False)

    service_type = db.Column(db.String(30))     # Consultation / Laboratory / Pharmacy / Other
    description = db.Column(db.String(255))
    reference_id = db.Column(db.String(30))     # e.g. CONS1001, LAB1001, PHAR1001
    amount = db.Column(db.Numeric(10, 2), default=0)

    def __repr__(self):
        return f"<BillItem {self.service_type} {self.amount}>"
