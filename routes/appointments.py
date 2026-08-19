from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from models import db
from models.appointment import Appointment
from models.patient import Patient
from models.doctor import Doctor
from models.activity_log import log_activity

appointments_bp = Blueprint("appointments", __name__, url_prefix="/appointments")


@appointments_bp.route("/")
@login_required
def list_appointments():
    query = Appointment.query

    if current_user.role == "patient":
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        query = query.filter_by(patient_id=patient.id if patient else -1)
    elif current_user.role == "doctor":
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        query = query.filter_by(doctor_id=doctor.id if doctor else -1)
    # admin / nurse see everything

    appts = query.order_by(Appointment.appointment_date.desc()).all()
    return render_template("appointments_list.html", appointments=appts)


@appointments_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_appointment():
    patients = Patient.query.order_by(Patient.full_name).all()
    doctors = Doctor.query.order_by(Doctor.full_name).all()

    if request.method == "POST":
        patient_id = request.form.get("patient_id")
        doctor_id = request.form.get("doctor_id")
        appt_date = request.form.get("appointment_date")
        appt_time = request.form.get("appointment_time")
        reason = request.form.get("reason_for_visit", "").strip()

        # if a logged-in patient is booking for themselves, lock the patient field
        if current_user.role == "patient":
            self_patient = Patient.query.filter_by(user_id=current_user.id).first()
            if self_patient:
                patient_id = self_patient.id

        if not (patient_id and doctor_id and appt_date and appt_time):
            flash("Please fill in patient, doctor, date, and time.", "error")
            return render_template("appointment_form.html", patients=patients, doctors=doctors)

        appointment = Appointment(
            patient_id=int(patient_id),
            doctor_id=int(doctor_id),
            appointment_date=datetime.strptime(appt_date, "%Y-%m-%d").date(),
            appointment_time=datetime.strptime(appt_time, "%H:%M").time(),
            reason_for_visit=reason,
            status="Scheduled",
        )
        db.session.add(appointment)
        db.session.flush()
        log_activity("Appointment Booked",
                      f"Appointment booked for {appointment.patient.full_name} with Dr. {appointment.doctor.full_name}",
                      user_id=current_user.id, icon="appointment")
        db.session.commit()
        return render_template("appointment_confirmation.html", appointment=appointment)

    return render_template("appointment_form.html", patients=patients, doctors=doctors)


@appointments_bp.route("/<int:appointment_id>/status", methods=["POST"])
@login_required
def update_status(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    new_status = request.form.get("status")
    if new_status in ("Scheduled", "Completed", "Cancelled", "No-show"):
        appointment.status = new_status
        if new_status == "Cancelled":
            log_activity("Appointment Cancelled",
                          f"Appointment for {appointment.patient.full_name} was cancelled",
                          user_id=current_user.id, icon="cancel")
        db.session.commit()
        flash("Appointment status updated.", "success")
    return redirect(url_for("appointments.list_appointments"))
