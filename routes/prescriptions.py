from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from models import db
from models.patient import Patient
from models.doctor import Doctor
from models.prescription import Prescription, PrescriptionItem
from models.activity_log import log_activity
from routes.utils import roles_required

prescriptions_bp = Blueprint("prescriptions", __name__, url_prefix="/prescriptions")


@prescriptions_bp.route("/")
@login_required
def list_prescriptions():
    if current_user.role == "patient":
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        prescriptions = patient.prescriptions if patient else []
    else:
        prescriptions = Prescription.query.order_by(Prescription.prescription_date.desc()).limit(50).all()
    return render_template("prescriptions_list.html", prescriptions=prescriptions)


@prescriptions_bp.route("/new", methods=["GET", "POST"])
@login_required
@roles_required("admin", "doctor")
def new_prescription():
    patients = Patient.query.order_by(Patient.full_name).all()
    doctors = Doctor.query.order_by(Doctor.full_name).all()

    if request.method == "POST":
        prescription = Prescription(
            patient_id=request.form.get("patient_id"),
            doctor_id=request.form.get("doctor_id"),
            prescription_date=datetime.strptime(request.form.get("prescription_date"), "%Y-%m-%d").date()
            if request.form.get("prescription_date") else date.today(),
            diagnosis=request.form.get("diagnosis"),
            special_instructions=request.form.get("special_instructions"),
        )
        db.session.add(prescription)
        db.session.flush()  # get prescription.id before commit

        med_names = request.form.getlist("medicine_name[]")
        dosages = request.form.getlist("dosage[]")
        frequencies = request.form.getlist("frequency[]")
        durations = request.form.getlist("duration[]")

        for name, dosage, freq, dur in zip(med_names, dosages, frequencies, durations):
            if name.strip():
                db.session.add(PrescriptionItem(
                    prescription_id=prescription.id,
                    medicine_name=name.strip(),
                    dosage=dosage,
                    frequency=freq,
                    duration=dur,
                ))
        log_activity("Prescription Generated",
                      f"Dr. {prescription.doctor.full_name} issued a prescription for {prescription.patient.full_name}",
                      user_id=current_user.id, icon="prescription")
        db.session.commit()
        return redirect(url_for("prescriptions.view_prescription", prescription_id=prescription.id))

    return render_template("prescription_form.html", patients=patients, doctors=doctors)


@prescriptions_bp.route("/<int:prescription_id>")
@login_required
def view_prescription(prescription_id):
    prescription = Prescription.query.get_or_404(prescription_id)
    return render_template("prescription_view.html", prescription=prescription)
