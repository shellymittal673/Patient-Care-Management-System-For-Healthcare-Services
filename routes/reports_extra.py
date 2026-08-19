import csv
import io
from collections import Counter, defaultdict
from datetime import date

from flask import Blueprint, render_template, Response
from flask_login import login_required

from models.patient import Patient
from models.doctor import Doctor
from models.appointment import Appointment
from models.consultation import Consultation
from models.prescription import Prescription
from routes.utils import roles_required

reports_extra_bp = Blueprint("reports_extra", __name__, url_prefix="/reports-extra")

REPORT_TYPES = [
    {"key": "patients", "name": "Patient Report", "desc": "All registered patients with demographics"},
    {"key": "appointments", "name": "Appointment Report", "desc": "All appointments with status breakdown"},
    {"key": "consultations", "name": "Consultation Report", "desc": "All consultations with diagnosis"},
    {"key": "prescriptions", "name": "Prescription Report", "desc": "All prescriptions issued"},
    {"key": "doctor_performance", "name": "Doctor Performance Report", "desc": "Consultation count per doctor"},
    {"key": "department", "name": "Department-wise Report", "desc": "Doctors and consultations grouped by specialization"},
    {"key": "monthly", "name": "Monthly Hospital Report", "desc": "Registrations, appointments, consultations this month"},
]


def _build_rows(report_key):
    """Returns (headers, rows) for the requested report — real DB data only."""
    if report_key == "patients":
        headers = ["Patient ID", "Full Name", "Age", "Gender", "Phone", "Blood Group", "Registered On"]
        rows = [[f"PAT{p.id:04d}", p.full_name, p.age, p.gender, p.contact_number,
                 p.blood_group, p.registration_date] for p in Patient.query.order_by(Patient.id).all()]

    elif report_key == "appointments":
        headers = ["Patient", "Doctor", "Date", "Time", "Reason", "Status"]
        rows = [[a.patient.full_name, f"Dr. {a.doctor.full_name}", a.appointment_date,
                 a.appointment_time, a.reason_for_visit, a.status]
                for a in Appointment.query.order_by(Appointment.appointment_date.desc()).all()]

    elif report_key == "consultations":
        headers = ["Patient", "Doctor", "Date", "Diagnosis", "Symptoms"]
        rows = [[c.patient.full_name, f"Dr. {c.doctor.full_name}", c.consultation_date,
                 c.diagnosis, c.symptoms] for c in Consultation.query.order_by(Consultation.consultation_date.desc()).all()]

    elif report_key == "prescriptions":
        headers = ["Patient", "Doctor", "Date", "Diagnosis", "Medicines"]
        rows = [[p.patient.full_name, f"Dr. {p.doctor.full_name}", p.prescription_date, p.diagnosis,
                 ", ".join(i.medicine_name for i in p.items)]
                for p in Prescription.query.order_by(Prescription.prescription_date.desc()).all()]

    elif report_key == "doctor_performance":
        headers = ["Doctor", "Specialization", "Consultations", "Appointments"]
        rows = [[f"Dr. {d.full_name}", d.specialization, len(d.consultations), len(d.appointments)]
                for d in Doctor.query.order_by(Doctor.full_name).all()]

    elif report_key == "department":
        headers = ["Department / Specialization", "Doctors", "Total Consultations"]
        by_spec = defaultdict(lambda: {"doctors": 0, "consultations": 0})
        for d in Doctor.query.all():
            spec = d.specialization or "General"
            by_spec[spec]["doctors"] += 1
            by_spec[spec]["consultations"] += len(d.consultations)
        rows = [[spec, v["doctors"], v["consultations"]] for spec, v in sorted(by_spec.items())]

    elif report_key == "monthly":
        today = date.today()
        headers = ["Metric", "Count (This Month)"]
        patients_this_month = Patient.query.filter(
            Patient.registration_date >= today.replace(day=1)).count()
        appts_this_month = Appointment.query.filter(
            Appointment.appointment_date >= today.replace(day=1)).count()
        consults_this_month = Consultation.query.filter(
            Consultation.consultation_date >= today.replace(day=1)).count()
        rows = [
            ["New Patient Registrations", patients_this_month],
            ["Appointments Booked", appts_this_month],
            ["Consultations Completed", consults_this_month],
        ]
    else:
        headers, rows = [], []

    return headers, rows


@reports_extra_bp.route("/")
@login_required
@roles_required("admin", "doctor")
def hub():
    return render_template("reports_hub.html", report_types=REPORT_TYPES)


@reports_extra_bp.route("/<report_key>")
@login_required
@roles_required("admin", "doctor")
def view_report(report_key):
    meta = next((r for r in REPORT_TYPES if r["key"] == report_key), None)
    if not meta:
        return "Unknown report type", 404
    headers, rows = _build_rows(report_key)
    return render_template("report_view.html", meta=meta, headers=headers, rows=rows)


@reports_extra_bp.route("/<report_key>/export.csv")
@login_required
@roles_required("admin", "doctor")
def export_csv(report_key):
    meta = next((r for r in REPORT_TYPES if r["key"] == report_key), None)
    if not meta:
        return "Unknown report type", 404
    headers, rows = _build_rows(report_key)

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(headers)
    writer.writerows(rows)

    return Response(
        buf.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={report_key}_report.csv"},
    )
