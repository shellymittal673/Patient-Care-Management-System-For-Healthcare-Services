from datetime import date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from models import db
from models.notification import Notification
from models.appointment import Appointment
from models.lab_test import LabTest
from models.patient import Patient
from routes.utils import roles_required

notifications_bp = Blueprint("notifications", __name__, url_prefix="/notifications")


@notifications_bp.route("/")
@login_required
def dashboard():
    notifications = Notification.query.order_by(Notification.created_at.desc()).limit(100).all()
    total = Notification.query.count()
    unread = Notification.query.filter(Notification.status != "Read").count()
    delivered = Notification.query.filter(Notification.status == "Delivered").count()
    failed = Notification.query.filter(Notification.status == "Failed").count()
    success_rate = round((delivered / total) * 100) if total else 0

    return render_template(
        "notification_dashboard.html",
        notifications=notifications, total=total, unread=unread,
        delivered=delivered, failed=failed, success_rate=success_rate,
    )


@notifications_bp.route("/<int:notification_id>/read", methods=["POST"])
@login_required
def mark_read(notification_id):
    n = Notification.query.get_or_404(notification_id)
    n.status = "Read"
    db.session.commit()
    return redirect(url_for("notifications.dashboard"))


@notifications_bp.route("/mark-all-read", methods=["POST"])
@login_required
def mark_all_read():
    Notification.query.filter(Notification.status != "Read").update({"status": "Read"})
    db.session.commit()
    flash("All notifications marked as read.", "success")
    return redirect(url_for("notifications.dashboard"))


@notifications_bp.route("/generate", methods=["POST"])
@login_required
@roles_required("admin")
def generate():
    """Scan real data for things worth notifying about (Milestone 3 Day 5),
    so this isn't just static demo rows — it reflects actual appointments
    and lab results in the system."""
    created = 0
    tomorrow = date.today() + timedelta(days=1)

    upcoming = Appointment.query.filter(Appointment.appointment_date.in_([date.today(), tomorrow])).all()
    for a in upcoming:
        msg = f"Your appointment with Dr. {a.doctor.full_name} is scheduled on {a.appointment_date} at {a.appointment_time}."
        exists = Notification.query.filter_by(patient_id=a.patient_id, message=msg).first()
        if not exists:
            db.session.add(Notification(patient_id=a.patient_id, notif_type="Appointment Reminder",
                                         message=msg, delivery_method="In-App"))
            created += 1

    ready_labs = LabTest.query.filter_by(status="Completed").limit(20).all()
    for t in ready_labs:
        msg = f"Your {t.test_type} report is available. Please check."
        exists = Notification.query.filter_by(patient_id=t.patient_id, message=msg).first()
        if not exists:
            db.session.add(Notification(patient_id=t.patient_id, notif_type="Lab Report",
                                         message=msg, delivery_method="In-App"))
            created += 1

    db.session.commit()
    flash(f"Generated {created} new notification(s) from current data.", "success")
    return redirect(url_for("notifications.dashboard"))


@notifications_bp.route("/send-test", methods=["POST"])
@login_required
@roles_required("admin")
def send_test():
    patient = Patient.query.order_by(Patient.id).first()
    if patient:
        db.session.add(Notification(
            patient_id=patient.id, notif_type="General",
            message=f"This is a test notification sent to {patient.full_name}.",
            delivery_method="In-App", status="Delivered",
        ))
        db.session.commit()
        flash("Test notification sent.", "success")
    return redirect(url_for("notifications.dashboard"))
