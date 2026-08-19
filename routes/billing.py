from datetime import date, datetime
from decimal import Decimal
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from models import db
from models.patient import Patient
from models.consultation import Consultation
from models.lab_test import LabTest
from models.medicine import DispenseRecord
from models.billing import Bill, BillItem
from models.activity_log import log_activity
from routes.utils import roles_required

billing_bp = Blueprint("billing", __name__, url_prefix="/billing")

CONSULTATION_FEE = Decimal("500.00")
LAB_TEST_FEE = Decimal("350.00")


@billing_bp.route("/")
@login_required
def list_bills():
    bills = Bill.query.order_by(Bill.created_at.desc()).limit(50).all()
    return render_template("billing_list.html", bills=bills)


@billing_bp.route("/new", methods=["GET"])
@login_required
@roles_required("admin", "nurse")
def new_bill():
    patients = Patient.query.order_by(Patient.full_name).all()
    patient = None
    billable_items = []

    patient_id = request.args.get("patient_id")
    if patient_id:
        patient = Patient.query.get(int(patient_id))
        if patient:
            already_billed_refs = {
                item.reference_id for bill in patient.bills for item in bill.items
            }
            for c in patient.consultations:
                ref = f"CONS{c.id:04d}"
                if ref not in already_billed_refs:
                    billable_items.append({
                        "type": "Consultation", "description": f"Consultation with Dr. {c.doctor.full_name}",
                        "ref": ref, "date": c.consultation_date, "amount": CONSULTATION_FEE,
                    })
            for t in patient.lab_tests:
                ref = f"LAB{t.id:04d}"
                if ref not in already_billed_refs:
                    billable_items.append({
                        "type": "Laboratory", "description": t.test_type,
                        "ref": ref, "date": t.request_date, "amount": LAB_TEST_FEE,
                    })
            for d in patient.dispense_records:
                ref = f"PHAR{d.id:04d}"
                if ref not in already_billed_refs:
                    billable_items.append({
                        "type": "Pharmacy", "description": f"{d.medicine.name} x{d.quantity}",
                        "ref": ref, "date": d.dispensed_at.date(),
                        "amount": (d.medicine.unit_price or 0) * d.quantity,
                    })
            billable_items.sort(key=lambda x: x["date"], reverse=True)

    return render_template("billing_form.html", patients=patients, patient=patient,
                            billable_items=billable_items)


@billing_bp.route("/create", methods=["POST"])
@login_required
@roles_required("admin", "nurse")
def create_bill():
    patient_id = request.form.get("patient_id")
    selected_refs = request.form.getlist("item_ref[]")
    types = request.form.getlist("item_type[]")
    descriptions = request.form.getlist("item_desc[]")
    amounts = request.form.getlist("item_amount[]")
    refs_all = request.form.getlist("item_ref_all[]")

    sub_total = Decimal("0")
    items_to_save = []
    for ref, itype, desc, amount in zip(refs_all, types, descriptions, amounts):
        if ref in selected_refs:
            amt = Decimal(amount or "0")
            sub_total += amt
            items_to_save.append((itype, desc, ref, amt))

    discount = Decimal(request.form.get("discount") or "0")
    tax = Decimal(request.form.get("tax") or "0")
    total = sub_total - discount + tax

    bill = Bill(
        patient_id=patient_id,
        bill_date=date.today(),
        sub_total=sub_total, discount=discount, tax=tax, total_amount=total,
        payment_method=request.form.get("payment_method"),
        payment_status=request.form.get("payment_status", "Paid"),
        transaction_id=request.form.get("transaction_id"),
    )
    db.session.add(bill)
    db.session.flush()

    for itype, desc, ref, amt in items_to_save:
        db.session.add(BillItem(bill_id=bill.id, service_type=itype, description=desc,
                                 reference_id=ref, amount=amt))

    if request.form.get("other_charges_amount"):
        other_amt = Decimal(request.form.get("other_charges_amount") or "0")
        if other_amt > 0:
            bill.sub_total += other_amt
            bill.total_amount += other_amt
            db.session.add(BillItem(bill_id=bill.id, service_type="Other",
                                     description=request.form.get("other_charges_desc", "Other Charges"),
                                     reference_id=f"OTH{bill.id:04d}", amount=other_amt))

    log_activity("Payment Received", f"Invoice BILL{bill.id:04d} generated for {bill.patient.full_name}",
                  user_id=current_user.id, icon="billing")
    db.session.commit()
    flash("Payment recorded successfully! Invoice generated successfully.", "success")
    return redirect(url_for("billing.view_bill", bill_id=bill.id))


@billing_bp.route("/<int:bill_id>")
@login_required
def view_bill(bill_id):
    bill = Bill.query.get_or_404(bill_id)
    return render_template("billing_invoice.html", bill=bill)
