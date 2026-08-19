from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from models import db
from models.patient import Patient
from models.appointment import Appointment
from models.activity_log import log_activity
from routes.utils import roles_required

patients_bp = Blueprint("patients", __name__, url_prefix="/patients")


def _calculate_age(dob):
    if not dob:
        return None
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


@patients_bp.route("/")
@login_required
@roles_required("admin", "doctor", "nurse")
def list_patients():
    patients = Patient.query.order_by(Patient.full_name).all()
    return render_template("patients_list.html", patients=patients)


@patients_bp.route("/new", methods=["GET", "POST"])
@login_required
@roles_required("admin", "nurse")
def new_patient():
    if request.method == "POST":
        patient = Patient(
            full_name=request.form.get("full_name", "").strip(),
            age=request.form.get("age") or None,
            gender=request.form.get("gender"),
            contact_number=request.form.get("contact_number"),
            email=request.form.get("email"),
            address=request.form.get("address"),
            blood_group=request.form.get("blood_group"),
            medical_history=request.form.get("medical_history"),
        )
        db.session.add(patient)
        db.session.flush()
        log_activity("Patient Registered", f"New patient registered — {patient.full_name} (PAT{patient.id:04d})",
                      user_id=current_user.id, icon="patient")
        db.session.commit()
        flash(f"Patient '{patient.full_name}' registered successfully.", "success")
        return redirect(url_for("patients.list_patients"))

    return render_template("patient_form.html", patient=None)


@patients_bp.route("/<int:patient_id>")
@login_required
def view_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    # a patient can only view their own profile; staff can view anyone's
    if current_user.role == "patient" and patient.user_id != current_user.id:
        flash("You can only view your own profile.", "error")
        return redirect(url_for("dashboard.home"))

    recent_appointments = (
        Appointment.query.filter_by(patient_id=patient.id)
        .order_by(Appointment.appointment_date.desc())
        .limit(5)
        .all()
    )
    return render_template("patient_profile.html", patient=patient,
                            appointments=recent_appointments)


@patients_bp.route("/<int:patient_id>/edit", methods=["GET", "POST"])
@login_required
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    if current_user.role == "patient" and patient.user_id != current_user.id:
        flash("You can only edit your own profile.", "error")
        return redirect(url_for("dashboard.home"))

    if request.method == "POST":
        patient.full_name = request.form.get("full_name", patient.full_name).strip()
        patient.age = request.form.get("age") or patient.age
        patient.gender = request.form.get("gender")
        patient.contact_number = request.form.get("contact_number")
        patient.email = request.form.get("email")
        patient.address = request.form.get("address")
        patient.blood_group = request.form.get("blood_group")
        patient.medical_history = request.form.get("medical_history")
        db.session.commit()
        flash("Patient profile updated.", "success")
        return redirect(url_for("patients.view_patient", patient_id=patient.id))

    return render_template("patient_form.html", patient=patient)


@patients_bp.route("/<int:patient_id>/delete", methods=["POST"])
@login_required
@roles_required("admin")
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    flash(f"Patient '{patient.full_name}' removed.", "success")
    return redirect(url_for("patients.list_patients"))
