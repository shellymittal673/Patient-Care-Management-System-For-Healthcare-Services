from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from models import db
from models.patient import Patient
from models.allergy import Allergy
from models.medication import Medication
from routes.utils import roles_required

ehr_bp = Blueprint("ehr", __name__, url_prefix="/ehr")


@ehr_bp.route("/")
@login_required
def list_ehr():
    """Milestone 2 Day 1 landing page — pick a patient to open their EHR."""
    if current_user.role == "patient":
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if patient:
            return redirect(url_for("ehr.view", patient_id=patient.id))
        patients = []
    else:
        patients = Patient.query.order_by(Patient.full_name).all()
    return render_template("ehr_list.html", patients=patients)


@ehr_bp.route("/<int:patient_id>")
@login_required
def view(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    return render_template("ehr_view.html", patient=patient)


@ehr_bp.route("/<int:patient_id>/edit-summary", methods=["GET", "POST"])
@login_required
@roles_required("admin", "doctor", "nurse")
def edit_summary(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if request.method == "POST":
        patient.height_cm = request.form.get("height_cm") or None
        patient.weight_kg = request.form.get("weight_kg") or None
        patient.smoking = request.form.get("smoking")
        patient.alcohol = request.form.get("alcohol")
        patient.chronic_diseases = request.form.get("chronic_diseases")
        patient.remarks = request.form.get("remarks")
        db.session.commit()
        flash("Medical summary updated.", "success")
        return redirect(url_for("ehr.view", patient_id=patient.id))
    return render_template("ehr_summary_form.html", patient=patient)


@ehr_bp.route("/<int:patient_id>/allergies/add", methods=["POST"])
@login_required
@roles_required("admin", "doctor", "nurse")
def add_allergy(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    allergen = request.form.get("allergen")
    reaction = request.form.get("reaction")
    if allergen:
        db.session.add(Allergy(patient_id=patient.id, allergen=allergen, reaction=reaction))
        db.session.commit()
        flash("Allergy added.", "success")
    return redirect(url_for("ehr.view", patient_id=patient.id))


@ehr_bp.route("/<int:patient_id>/medications/add", methods=["POST"])
@login_required
@roles_required("admin", "doctor", "nurse")
def add_medication(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    name = request.form.get("medicine_name")
    if name:
        db.session.add(Medication(
            patient_id=patient.id,
            medicine_name=name,
            dosage=request.form.get("dosage"),
            frequency=request.form.get("frequency"),
            start_date=date.today(),
        ))
        db.session.commit()
        flash("Medication added.", "success")
    return redirect(url_for("ehr.view", patient_id=patient.id))
