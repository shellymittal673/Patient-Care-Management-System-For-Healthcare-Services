from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from models import db
from models.feedback import Feedback
from models.patient import Patient
from models.doctor import Doctor
from models.activity_log import log_activity

feedback_bp = Blueprint("feedback", __name__, url_prefix="/feedback")


@feedback_bp.route("/")
@login_required
def list_feedback():
    if current_user.role == "patient":
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        entries = patient.feedback_entries if patient else []
        doctors = []
    else:
        query = Feedback.query
        doctor_id = request.args.get("doctor_id")
        rating = request.args.get("rating")
        if doctor_id:
            query = query.filter_by(doctor_id=doctor_id)
        if rating:
            query = query.filter(Feedback.rating_doctor == int(rating))
        entries = query.order_by(Feedback.created_at.desc()).all()
        doctors = Doctor.query.order_by(Doctor.full_name).all()

    all_ratings = [e.average_rating for e in Feedback.query.all() if e.average_rating]
    avg_satisfaction = round(sum(all_ratings) / len(all_ratings), 1) if all_ratings else None

    return render_template("feedback_list.html", entries=entries, doctors=doctors,
                            avg_satisfaction=avg_satisfaction,
                            selected_doctor=request.args.get("doctor_id", ""),
                            selected_rating=request.args.get("rating", ""))


@feedback_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_feedback():
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    doctors = Doctor.query.order_by(Doctor.full_name).all()

    if request.method == "POST":
        if not patient:
            flash("No patient profile linked to this account.", "error")
            return redirect(url_for("feedback.list_feedback"))

        entry = Feedback(
            patient_id=patient.id,
            doctor_id=request.form.get("doctor_id") or None,
            rating_doctor=int(request.form.get("rating_doctor") or 0) or None,
            rating_hospital=int(request.form.get("rating_hospital") or 0) or None,
            rating_lab=int(request.form.get("rating_lab") or 0) or None,
            rating_pharmacy=int(request.form.get("rating_pharmacy") or 0) or None,
            comments=request.form.get("comments"),
            feedback_date=date.today(),
        )
        db.session.add(entry)
        log_activity("Feedback Submitted", f"{patient.full_name} submitted feedback.",
                      user_id=current_user.id, icon="feedback")
        db.session.commit()
        flash("Thank you — your feedback has been recorded.", "success")
        return redirect(url_for("feedback.list_feedback"))

    return render_template("feedback_form.html", doctors=doctors)


@feedback_bp.route("/<int:feedback_id>")
@login_required
def view_feedback(feedback_id):
    entry = Feedback.query.get_or_404(feedback_id)
    return render_template("feedback_detail.html", entry=entry)
