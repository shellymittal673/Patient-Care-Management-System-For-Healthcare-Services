from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from models.patient import Patient
from models.consultation import Consultation
from models.prescription import Prescription
from models.lab_test import LabTest

medical_history_bp = Blueprint("medical_history", __name__, url_prefix="/medical-history")


@medical_history_bp.route("/")
@login_required
def list_patients():
    """Pick a patient to view their combined medical history (Milestone 2 Day 5)."""
    if current_user.role == "patient":
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if patient:
            return redirect(url_for("medical_history.view", patient_id=patient.id))
        patients = []
    else:
        patients = Patient.query.order_by(Patient.full_name).all()
    return render_template("medical_history_list.html", patients=patients)


@medical_history_bp.route("/<int:patient_id>")
@login_required
def view(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    # Build one combined, date-sorted timeline out of consultations,
    # prescriptions, and lab tests - this is what connects Milestone 1's
    # patient record to everything recorded across Milestone 2's modules.
    timeline = []
    for c in patient.consultations:
        timeline.append({
            "date": c.consultation_date, "type": "Consultation",
            "description": c.diagnosis or c.symptoms, "physician": c.doctor.full_name,
            "link": url_for("consultations.list_consultations"),
        })
    for p in patient.prescriptions:
        timeline.append({
            "date": p.prescription_date, "type": "Prescription",
            "description": p.diagnosis or "Prescription issued", "physician": p.doctor.full_name,
            "link": url_for("prescriptions.view_prescription", prescription_id=p.id),
        })
    for t in patient.lab_tests:
        timeline.append({
            "date": t.request_date, "type": "Laboratory Test",
            "description": f"{t.test_type} ({t.status})", "physician": t.doctor.full_name,
            "link": url_for("lab.view_report", test_id=t.id),
        })
    timeline.sort(key=lambda x: x["date"], reverse=True)

    return render_template("medical_history_view.html", patient=patient, timeline=timeline[:15])
