from flask import Blueprint, jsonify, request
from flask_login import login_required

from models import db
from models.patient import Patient
from models.doctor import Doctor
from models.consultation import Consultation
from models.prescription import Prescription
from models.lab_test import LabTest
from models.billing import Bill
from models.notification import Notification

api_bp = Blueprint("api", __name__, url_prefix="/api")


def patient_to_dict(p):
    return {
        "patient_id": f"P{p.id:04d}", "name": p.full_name, "age": p.age,
        "gender": p.gender, "phone": p.contact_number, "email": p.email,
        "address": p.address, "blood_group": p.blood_group,
    }


def doctor_to_dict(d):
    return {
        "doctor_id": f"D{d.id:04d}", "name": d.full_name, "specialization": d.specialization,
        "phone": d.phone_number, "email": d.email, "years_experience": d.years_experience,
    }


@api_bp.route("/patients", methods=["GET", "POST"])
@login_required
def patients():
    if request.method == "POST":
        data = request.get_json(force=True) or {}
        p = Patient(full_name=data.get("name"), age=data.get("age"), gender=data.get("gender"),
                    contact_number=data.get("phone"), email=data.get("email"))
        db.session.add(p)
        db.session.commit()
        return jsonify({"status": "success", "message": "Patient created", "data": patient_to_dict(p)}), 201

    rows = Patient.query.order_by(Patient.id).limit(50).all()
    return jsonify({"status": "success", "message": "Patients retrieved successfully",
                     "data": [patient_to_dict(p) for p in rows]})


@api_bp.route("/patients/<int:patient_id>", methods=["GET"])
@login_required
def patient_detail(patient_id):
    p = Patient.query.get_or_404(patient_id)
    return jsonify({"status": "success", "data": patient_to_dict(p)})


@api_bp.route("/doctors", methods=["GET", "POST"])
@login_required
def doctors():
    if request.method == "POST":
        data = request.get_json(force=True) or {}
        d = Doctor(full_name=data.get("name"), specialization=data.get("specialization"),
                   phone_number=data.get("phone"), email=data.get("email"))
        db.session.add(d)
        db.session.commit()
        return jsonify({"status": "success", "message": "Doctor created", "data": doctor_to_dict(d)}), 201

    rows = Doctor.query.order_by(Doctor.id).limit(50).all()
    return jsonify({"status": "success", "message": "Doctors retrieved successfully",
                     "data": [doctor_to_dict(d) for d in rows]})


@api_bp.route("/consultations", methods=["GET"])
@login_required
def consultations():
    rows = Consultation.query.order_by(Consultation.id.desc()).limit(50).all()
    return jsonify({"status": "success", "message": "Consultations retrieved successfully", "data": [
        {"consultation_id": f"CONS{c.id:04d}", "patient": c.patient.full_name, "doctor": c.doctor.full_name,
         "date": str(c.consultation_date), "diagnosis": c.diagnosis} for c in rows
    ]})


@api_bp.route("/prescriptions", methods=["GET"])
@login_required
def prescriptions():
    rows = Prescription.query.order_by(Prescription.id.desc()).limit(50).all()
    return jsonify({"status": "success", "message": "Prescriptions retrieved successfully", "data": [
        {"prescription_id": f"PRS{p.id:04d}", "patient": p.patient.full_name, "doctor": p.doctor.full_name,
         "date": str(p.prescription_date), "diagnosis": p.diagnosis,
         "medicines": [item.medicine_name for item in p.items]} for p in rows
    ]})


@api_bp.route("/laboratory", methods=["GET"])
@login_required
def laboratory():
    rows = LabTest.query.order_by(LabTest.id.desc()).limit(50).all()
    return jsonify({"status": "success", "message": "Lab tests retrieved successfully", "data": [
        {"test_id": f"TR{t.id:05d}", "patient": t.patient.full_name, "test_type": t.test_type,
         "status": t.status, "request_date": str(t.request_date)} for t in rows
    ]})


@api_bp.route("/billing", methods=["GET"])
@login_required
def billing():
    rows = Bill.query.order_by(Bill.id.desc()).limit(50).all()
    return jsonify({"status": "success", "message": "Bills retrieved successfully", "data": [
        {"bill_id": f"BILL{b.id:04d}", "patient": b.patient.full_name,
         "total_amount": float(b.total_amount), "status": b.payment_status} for b in rows
    ]})


@api_bp.route("/notifications", methods=["GET", "POST"])
@login_required
def notifications():
    if request.method == "POST":
        data = request.get_json(force=True) or {}
        n = Notification(patient_id=data.get("patient_id"), notif_type=data.get("notif_type", "General"),
                          message=data.get("message"), delivery_method=data.get("delivery_method", "In-App"))
        db.session.add(n)
        db.session.commit()
        return jsonify({"status": "success", "message": "Notification created"}), 201

    rows = Notification.query.order_by(Notification.id.desc()).limit(50).all()
    return jsonify({"status": "success", "message": "Notifications retrieved successfully", "data": [
        {"notification_id": f"NOT{n.id:04d}",
         "patient": n.patient.full_name if n.patient else None,
         "type": n.notif_type, "message": n.message, "status": n.status} for n in rows
    ]})
