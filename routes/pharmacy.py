from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from models import db
from models.medicine import Medicine, DispenseRecord
from models.patient import Patient
from models.prescription import Prescription
from routes.utils import roles_required

pharmacy_bp = Blueprint("pharmacy", __name__, url_prefix="/pharmacy")


@pharmacy_bp.route("/")
@login_required
def dashboard():
    q = request.args.get("q", "").strip()
    medicines_query = Medicine.query
    if q:
        medicines_query = medicines_query.filter(Medicine.name.ilike(f"%{q}%"))
    medicines = medicines_query.order_by(Medicine.name).all()

    all_medicines = Medicine.query.all()
    total_medicines = len(all_medicines)
    available_stock = sum(m.stock or 0 for m in all_medicines)
    low_stock = sum(1 for m in all_medicines if m.status == "Low Stock")
    expired = sum(1 for m in all_medicines if m.status == "Expired")
    dispensed_today = DispenseRecord.query.filter(
        db.func.date(DispenseRecord.dispensed_at) == date.today()
    ).count()

    patients = Patient.query.order_by(Patient.full_name).all()

    return render_template(
        "pharmacy_dashboard.html",
        medicines=medicines, q=q,
        total_medicines=total_medicines, available_stock=available_stock,
        low_stock=low_stock, expired=expired, dispensed_today=dispensed_today,
        patients=patients,
    )


@pharmacy_bp.route("/add", methods=["POST"])
@login_required
@roles_required("admin", "pharmacist")
def add_medicine():
    name = request.form.get("name")
    if name:
        db.session.add(Medicine(
            name=name,
            category=request.form.get("category"),
            manufacturer=request.form.get("manufacturer"),
            stock=int(request.form.get("stock") or 0),
            unit_price=float(request.form.get("unit_price") or 0),
            expiry_date=datetime.strptime(request.form.get("expiry_date"), "%Y-%m-%d").date()
            if request.form.get("expiry_date") else None,
        ))
        db.session.commit()
        flash(f'"{name}" added to inventory.', "success")
    return redirect(url_for("pharmacy.dashboard"))


@pharmacy_bp.route("/<int:medicine_id>/update-stock", methods=["POST"])
@login_required
@roles_required("admin", "pharmacist")
def update_stock(medicine_id):
    medicine = Medicine.query.get_or_404(medicine_id)
    new_stock = request.form.get("stock")
    if new_stock is not None:
        medicine.stock = int(new_stock)
        db.session.commit()
        flash(f"Stock updated for {medicine.name}.", "success")
    return redirect(url_for("pharmacy.dashboard"))


@pharmacy_bp.route("/<int:medicine_id>/delete", methods=["POST"])
@login_required
@roles_required("admin")
def delete_medicine(medicine_id):
    medicine = Medicine.query.get_or_404(medicine_id)
    db.session.delete(medicine)
    db.session.commit()
    flash("Medicine removed from inventory.", "success")
    return redirect(url_for("pharmacy.dashboard"))


@pharmacy_bp.route("/dispense", methods=["POST"])
@login_required
@roles_required("admin", "pharmacist")
def dispense():
    patient_id = request.form.get("patient_id")
    medicine_id = request.form.get("medicine_id")
    quantity = int(request.form.get("quantity") or 0)

    medicine = Medicine.query.get_or_404(medicine_id)
    if quantity <= 0 or quantity > (medicine.stock or 0):
        flash("Invalid quantity — check available stock.", "error")
        return redirect(url_for("pharmacy.dashboard"))

    medicine.stock -= quantity
    record = DispenseRecord(
        patient_id=patient_id, medicine_id=medicine.id,
        quantity=quantity, dispensed_by=current_user.id,
    )
    db.session.add(record)
    db.session.commit()
    flash(f"Dispensed {quantity} unit(s) of {medicine.name} successfully.", "success")
    return redirect(url_for("pharmacy.dashboard"))
