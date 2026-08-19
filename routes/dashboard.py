from datetime import date, timedelta
from collections import Counter
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user

from models.patient import Patient
from models.doctor import Doctor
from models.appointment import Appointment
from models.consultation import Consultation
from models.lab_test import LabTest
from models.billing import Bill
from models.notification import Notification
from models.activity_log import ActivityLog
from models.user import User

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def home():
    """Route each role to its own dashboard view."""
    if current_user.role == "admin":
        return admin_dashboard()
    elif current_user.role == "doctor":
        return doctor_dashboard()
    elif current_user.role == "nurse":
        return nurse_dashboard()
    elif current_user.role == "pharmacist":
        return redirect(url_for("pharmacy.dashboard"))
    else:
        return patient_dashboard()


def admin_dashboard():
    total_patients = Patient.query.count()
    total_doctors = Doctor.query.count()
    total_nurses = User.query.filter_by(role="nurse").count()
    todays_appointments_count = Appointment.query.filter_by(appointment_date=date.today()).count()

    # ---- Milestone 4: extra stat cards, all real counts ----
    completed_consultations = Consultation.query.count()
    cancelled_appointments = Appointment.query.filter_by(status="Cancelled").count()
    pending_lab_reports = LabTest.query.filter(LabTest.status != "Completed").count()
    total_revenue = sum(float(b.total_amount or 0) for b in Bill.query.filter_by(payment_status="Paid").all())
    unread_notifications = Notification.query.filter(Notification.status != "Read").count()

    # ---- Appointments Overview: last 7 days, count per day ----
    today = date.today()
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    appts_by_day = Counter(
        a.appointment_date for a in Appointment.query.filter(
            Appointment.appointment_date >= last_7_days[0]
        ).all()
    )
    chart_labels = [d.strftime("%b %d") for d in last_7_days]
    chart_counts = [appts_by_day.get(d, 0) for d in last_7_days]

    # ---- Department Wise Doctors: group by specialization ----
    spec_counts = Counter(
        (d.specialization or "Other") for d in Doctor.query.all()
    )
    # keep top 4 + bucket the rest as "Other"
    top_specs = spec_counts.most_common(4)
    other_count = sum(c for _, c in spec_counts.most_common()[4:])
    dept_labels = [s for s, _ in top_specs]
    dept_counts = [c for _, c in top_specs]
    if other_count:
        dept_labels.append("Other")
        dept_counts.append(other_count)

    # ---- Milestone 4: Monthly Patient Registrations (last 6 months) ----
    months = []
    d = today.replace(day=1)
    for _ in range(6):
        months.append(d)
        d = (d - timedelta(days=1)).replace(day=1)
    months.reverse()
    reg_by_month = Counter()
    for p in Patient.query.all():
        if p.registration_date:
            key = p.registration_date.replace(day=1)
            reg_by_month[key] += 1
    reg_labels = [m.strftime("%b") for m in months]
    reg_counts = [reg_by_month.get(m, 0) for m in months]

    # ---- Milestone 4: Patient Demographics by gender ----
    gender_counts = Counter((p.gender or "Other") for p in Patient.query.all())
    demo_labels = list(gender_counts.keys())
    demo_counts = list(gender_counts.values())

    # ---- Milestone 4: Doctor-wise Consultation Count (top 5) ----
    doc_consult_counts = sorted(
        ((d.full_name, len(d.consultations)) for d in Doctor.query.all()),
        key=lambda x: x[1], reverse=True
    )[:5]
    doc_labels = [f"Dr. {n}" for n, _ in doc_consult_counts]
    doc_counts = [c for _, c in doc_consult_counts]

    # ---- Recent Patient Registrations ----
    recent_patients = (
        Patient.query.order_by(Patient.registration_date.desc(), Patient.id.desc())
        .limit(5).all()
    )

    # ---- Today's Appointments ----
    todays_appointments = (
        Appointment.query.filter_by(appointment_date=date.today())
        .order_by(Appointment.appointment_time)
        .limit(5).all()
    )

    # ---- Milestone 4: Recent System Activity (real audit log) ----
    recent_activity = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(8).all()

    return render_template(
        "dashboard_admin.html",
        total_patients=total_patients,
        total_doctors=total_doctors,
        total_nurses=total_nurses,
        todays_appointments_count=todays_appointments_count,
        completed_consultations=completed_consultations,
        cancelled_appointments=cancelled_appointments,
        pending_lab_reports=pending_lab_reports,
        total_revenue=total_revenue,
        unread_notifications=unread_notifications,
        chart_labels=chart_labels,
        chart_counts=chart_counts,
        dept_labels=dept_labels,
        dept_counts=dept_counts,
        reg_labels=reg_labels,
        reg_counts=reg_counts,
        demo_labels=demo_labels,
        demo_counts=demo_counts,
        doc_labels=doc_labels,
        doc_counts=doc_counts,
        recent_patients=recent_patients,
        todays_appointments=todays_appointments,
        recent_activity=recent_activity,
    )


def doctor_dashboard():
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    appointments = []
    if doctor:
        appointments = (
            Appointment.query.filter_by(doctor_id=doctor.id)
            .order_by(Appointment.appointment_date.desc())
            .limit(10)
            .all()
        )
    return render_template("dashboard_doctor.html", doctor=doctor, appointments=appointments)


def nurse_dashboard():
    total_patients = Patient.query.count()
    todays_appointments = Appointment.query.filter_by(appointment_date=date.today()).all()
    return render_template(
        "dashboard_nurse.html",
        total_patients=total_patients,
        todays_appointments=todays_appointments,
    )


def patient_dashboard():
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    appointments = []
    if patient:
        appointments = (
            Appointment.query.filter_by(patient_id=patient.id)
            .order_by(Appointment.appointment_date.desc())
            .limit(10)
            .all()
        )
    return render_template("dashboard_patient.html", patient=patient, appointments=appointments)


@dashboard_bp.route("/reports")
@login_required
def reports():
    total_patients = Patient.query.count()
    total_doctors = Doctor.query.count()
    total_nurses = User.query.filter_by(role="nurse").count()
    total_appointments = Appointment.query.count()
    completed = Appointment.query.filter_by(status="Completed").count()
    cancelled = Appointment.query.filter_by(status="Cancelled").count()
    scheduled = Appointment.query.filter_by(status="Scheduled").count()
    no_show = Appointment.query.filter_by(status="No-show").count()

    # ---- Reports & Search: look up a patient by ID or name ----
    search_by = request.args.get("search_by", "id")
    search_value = request.args.get("search_value", "").strip()
    found_patient = None
    searched = bool(search_value)
    if search_value:
        if search_by == "id":
            digits = "".join(ch for ch in search_value if ch.isdigit())
            if digits:
                found_patient = Patient.query.get(int(digits))
        else:
            found_patient = Patient.query.filter(Patient.full_name.ilike(f"%{search_value}%")).first()

    return render_template(
        "reports.html",
        total_patients=total_patients,
        total_doctors=total_doctors,
        total_nurses=total_nurses,
        total_appointments=total_appointments,
        completed=completed,
        cancelled=cancelled,
        scheduled=scheduled,
        no_show=no_show,
        generated_on=date.today(),
        search_by=search_by,
        search_value=search_value,
        found_patient=found_patient,
        searched=searched,
    )


@dashboard_bp.route("/reports/patient/<int:patient_id>")
@login_required
def patient_report(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    return render_template("patient_report.html", patient=patient, generated_on=date.today())
