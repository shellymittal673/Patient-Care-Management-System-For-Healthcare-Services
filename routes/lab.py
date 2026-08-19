import os
from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from models import db
from models.patient import Patient
from models.doctor import Doctor
from models.lab_test import LabTest
from models.activity_log import log_activity
from routes.utils import roles_required

lab_bp = Blueprint("lab", __name__, url_prefix="/lab")

UPLOAD_DIR = os.path.join("static", "uploads", "lab_reports")


@lab_bp.route("/")
@login_required
def dashboard():
    if current_user.role == "patient":
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        tests = patient.lab_tests if patient else []
    else:
        tests = LabTest.query.order_by(LabTest.request_date.desc()).limit(100).all()

    total = len(tests) if current_user.role == "patient" else LabTest.query.count()
    pending = LabTest.query.filter_by(status="Pending").count()
    completed = LabTest.query.filter_by(status="Completed").count()
    return render_template("lab_dashboard.html", tests=tests,
                            total=total, pending=pending, completed=completed)


@lab_bp.route("/new", methods=["GET", "POST"])
@login_required
@roles_required("admin", "doctor")
def new_request():
    patients = Patient.query.order_by(Patient.full_name).all()
    doctors = Doctor.query.order_by(Doctor.full_name).all()

    if request.method == "POST":
        test = LabTest(
            patient_id=request.form.get("patient_id"),
            doctor_id=request.form.get("doctor_id"),
            test_type=request.form.get("test_type"),
            request_date=datetime.strptime(request.form.get("request_date"), "%Y-%m-%d").date()
            if request.form.get("request_date") else date.today(),
            status="Pending",
        )
        db.session.add(test)
        db.session.commit()
        flash("Lab test request created.", "success")
        return redirect(url_for("lab.dashboard"))

    return render_template("lab_request_form.html", patients=patients, doctors=doctors)


@lab_bp.route("/<int:test_id>/upload", methods=["GET", "POST"])
@login_required
@roles_required("admin", "doctor", "nurse")
def upload_result(test_id):
    test = LabTest.query.get_or_404(test_id)

    if request.method == "POST":
        test.result_summary = request.form.get("result_summary")
        test.remarks = request.form.get("remarks")
        test.status = "Completed"
        test.uploaded_at = datetime.utcnow()

        file = request.files.get("report_file")
        if file and file.filename:
            os.makedirs(UPLOAD_DIR, exist_ok=True)
            filename = secure_filename(f"test{test.id}_{file.filename}")
            file.save(os.path.join(UPLOAD_DIR, filename))
            test.report_filename = filename

        log_activity("Lab Report Uploaded",
                      f"Test: {test.test_type}, Patient: {test.patient.full_name}",
                      user_id=current_user.id, icon="lab")
        db.session.commit()
        flash("Lab report uploaded and saved. Patient's EHR has been updated.", "success")
        return redirect(url_for("lab.dashboard"))

    return render_template("lab_upload_form.html", test=test)


@lab_bp.route("/<int:test_id>/report")
@login_required
def view_report(test_id):
    test = LabTest.query.get_or_404(test_id)
    return render_template("lab_report_view.html", test=test)
