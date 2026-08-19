from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from models import db
from models.patient import Patient
from models.doctor import Doctor
from models.consultation import Consultation
from models.activity_log import log_activity
from routes.utils import roles_required

consultations_bp = Blueprint("consultations", __name__, url_prefix="/consultations")


@consultations_bp.route("/")
@login_required
def list_consultations():
    if current_user.role == "patient":
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        consultations = patient.consultations if patient else []
    elif current_user.role == "doctor":
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        consultations = (
            Consultation.query.filter_by(doctor_id=doctor.id)
            .order_by(Consultation.consultation_date.desc()).all()
            if doctor else []
        )
    else:
        consultations = Consultation.query.order_by(Consultation.consultation_date.desc()).limit(50).all()
    return render_template("consultations_list.html", consultations=consultations)


@consultations_bp.route("/new", methods=["GET", "POST"])
@login_required
@roles_required("admin", "doctor", "nurse")
def new_consultation():
    patients = Patient.query.order_by(Patient.full_name).all()
    doctors = Doctor.query.order_by(Doctor.full_name).all()

    if request.method == "POST":
        consultation = Consultation(
            patient_id=request.form.get("patient_id"),
            doctor_id=request.form.get("doctor_id"),
            consultation_date=datetime.strptime(request.form.get("consultation_date"), "%Y-%m-%d").date()
            if request.form.get("consultation_date") else date.today(),
            symptoms=request.form.get("symptoms"),
            diagnosis=request.form.get("diagnosis"),
            treatment=request.form.get("treatment"),
        )
        db.session.add(consultation)
        db.session.flush()
        log_activity("Consultation Completed",
                      f"Dr. {consultation.doctor.full_name} completed a consultation with {consultation.patient.full_name}",
                      user_id=current_user.id, icon="consultation")
        db.session.commit()
        return render_template("consultation_summary.html", consultation=consultation)

    return render_template("consultation_form.html", patients=patients, doctors=doctors)
