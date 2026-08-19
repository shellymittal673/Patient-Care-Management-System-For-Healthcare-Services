from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from models import db
from models.doctor import Doctor
from routes.utils import roles_required

doctors_bp = Blueprint("doctors", __name__, url_prefix="/doctors")


@doctors_bp.route("/")
@login_required
def list_doctors():
    doctors = Doctor.query.order_by(Doctor.full_name).all()
    return render_template("doctors_list.html", doctors=doctors)


@doctors_bp.route("/new", methods=["GET", "POST"])
@login_required
@roles_required("admin")
def new_doctor():
    if request.method == "POST":
        doctor = Doctor(
            full_name=request.form.get("full_name", "").strip(),
            specialization=request.form.get("specialization"),
            qualification=request.form.get("qualification"),
            phone_number=request.form.get("phone_number"),
            email=request.form.get("email"),
            department=request.form.get("department"),
            hospital_branch=request.form.get("hospital_branch"),
            years_experience=request.form.get("years_experience") or None,
            available_time=request.form.get("available_time"),
        )
        db.session.add(doctor)
        db.session.commit()
        flash(f"Dr. {doctor.full_name} added successfully.", "success")
        return redirect(url_for("doctors.list_doctors"))

    return render_template("doctor_form.html", doctor=None)


@doctors_bp.route("/<int:doctor_id>/edit", methods=["GET", "POST"])
@login_required
@roles_required("admin")
def edit_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)

    if request.method == "POST":
        doctor.full_name = request.form.get("full_name", doctor.full_name).strip()
        doctor.specialization = request.form.get("specialization")
        doctor.qualification = request.form.get("qualification")
        doctor.phone_number = request.form.get("phone_number")
        doctor.email = request.form.get("email")
        doctor.department = request.form.get("department")
        doctor.hospital_branch = request.form.get("hospital_branch")
        doctor.years_experience = request.form.get("years_experience") or doctor.years_experience
        doctor.available_time = request.form.get("available_time")
        db.session.commit()
        flash(f"Dr. {doctor.full_name}'s details updated.", "success")
        return redirect(url_for("doctors.list_doctors"))

    return render_template("doctor_form.html", doctor=doctor)


@doctors_bp.route("/<int:doctor_id>/delete", methods=["POST"])
@login_required
@roles_required("admin")
def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    db.session.delete(doctor)
    db.session.commit()
    flash(f"Dr. {doctor.full_name} removed.", "success")
    return redirect(url_for("doctors.list_doctors"))
