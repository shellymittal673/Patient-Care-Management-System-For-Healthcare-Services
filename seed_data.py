"""
Run this once after creating your MySQL database and tables, to populate
sample data: default login accounts for each role + real patients/doctors/
appointments from the dataset CSVs in database/.

Usage:
    python seed_data.py
"""
import csv
import os
from datetime import datetime, date

from app import create_app
from models import db
from models.user import User
from models.patient import Patient
from models.doctor import Doctor
from models.appointment import Appointment
from models.allergy import Allergy
from models.medication import Medication
from models.consultation import Consultation
from models.medical_background import PastIllness, PastSurgery, FamilyHistory
from models.medicine import Medicine, DispenseRecord
from models.billing import Bill, BillItem
from models.notification import Notification
from models.feedback import Feedback
from models.activity_log import ActivityLog

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "database")

# Keeps dataset code ("A001") -> our Appointment row, filled in by seed_appointments()
_appointment_code_map = {}


def create_default_logins():
    """One login per role so you can demo immediately."""
    defaults = [
        ("Admin User", "admin@pcms.com", "admin123", "admin"),
        ("Dr. Demo", "doctor@pcms.com", "doctor123", "doctor"),
        ("Nurse Demo", "nurse@pcms.com", "nurse123", "nurse"),
        ("Patient Demo", "patient@pcms.com", "patient123", "patient"),
        ("Pharmacist Demo", "pharmacist@pcms.com", "pharma123", "pharmacist"),
    ]
    for full_name, email, password, role in defaults:
        if User.query.filter_by(email=email).first():
            continue
        user = User(full_name=full_name, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
    db.session.commit()
    print("Default login accounts created (admin/doctor/nurse/patient/pharmacist @pcms.com).")


def seed_doctors():
    path = os.path.join(DATA_DIR, "doctors.csv")
    count = 0
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            full_name = f"{row['first_name']} {row['last_name']}"
            if Doctor.query.filter_by(full_name=full_name, email=row["email"]).first():
                continue
            doctor = Doctor(
                full_name=full_name,
                specialization=row["specialization"],
                phone_number=row["phone_number"],
                years_experience=int(row["years_experience"]) if row["years_experience"] else None,
                hospital_branch=row["hospital_branch"],
                email=row["email"],
            )
            db.session.add(doctor)
            count += 1
    db.session.commit()
    print(f"Seeded {count} doctors.")


def seed_patients():
    path = os.path.join(DATA_DIR, "patients.csv")
    count = 0
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            full_name = f"{row['first_name']} {row['last_name']}"
            if Patient.query.filter_by(full_name=full_name, email=row["email"]).first():
                continue
            dob = datetime.strptime(row["date_of_birth"], "%Y-%m-%d").date() if row["date_of_birth"] else None
            age = None
            if dob:
                today = date.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            patient = Patient(
                full_name=full_name,
                age=age,
                date_of_birth=dob,
                gender="Male" if row["gender"] == "M" else "Female" if row["gender"] == "F" else row["gender"],
                contact_number=row["contact_number"],
                email=row["email"],
                address=row["address"],
                registration_date=datetime.strptime(row["registration_date"], "%Y-%m-%d").date()
                if row["registration_date"] else date.today(),
            )
            db.session.add(patient)
            count += 1
    db.session.commit()
    print(f"Seeded {count} patients.")


def seed_appointments():
    path = os.path.join(DATA_DIR, "appointments.csv")
    # Build lookup maps: dataset codes (P001, D001...) -> DB row order
    patients = Patient.query.order_by(Patient.id).all()
    doctors = Doctor.query.order_by(Doctor.id).all()

    # dataset patient_id "P001" -> index 0, "P002" -> index 1, etc.
    def code_to_index(code):
        return int(code[1:]) - 1

    count = 0
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            p_idx = code_to_index(row["patient_id"])
            d_idx = code_to_index(row["doctor_id"])
            if p_idx >= len(patients) or d_idx >= len(doctors):
                continue

            status_map = {
                "Scheduled": "Scheduled", "Completed": "Completed",
                "Cancelled": "Cancelled", "No-show": "No-show",
            }
            appt = Appointment(
                patient_id=patients[p_idx].id,
                doctor_id=doctors[d_idx].id,
                appointment_date=datetime.strptime(row["appointment_date"], "%Y-%m-%d").date(),
                appointment_time=datetime.strptime(row["appointment_time"], "%H:%M:%S").time(),
                reason_for_visit=row["reason_for_visit"],
                status=status_map.get(row["status"], "Scheduled"),
            )
            db.session.add(appt)
            db.session.flush()  # get appt.id so we can map it below
            _appointment_code_map[row["appointment_id"]] = appt
            count += 1
    db.session.commit()
    print(f"Seeded {count} appointments.")


def seed_consultations_from_treatments():
    """
    Milestone 2 connects to Milestone 1 here: each row in treatments.csv
    references an appointment (and therefore a patient + doctor already
    seeded above), so we turn each treatment into a Consultation record -
    exactly what the Consultation Management module produces by hand.
    """
    path = os.path.join(DATA_DIR, "treatments.csv")
    count = 0
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            appt = _appointment_code_map.get(row["appointment_id"])
            if not appt:
                continue
            consultation = Consultation(
                patient_id=appt.patient_id,
                doctor_id=appt.doctor_id,
                consultation_date=datetime.strptime(row["treatment_date"], "%Y-%m-%d").date(),
                symptoms=row["description"],
                diagnosis=row["treatment_type"],
                treatment=f"{row['treatment_type']} — {row['description']}",
            )
            db.session.add(consultation)
            count += 1
    db.session.commit()
    print(f"Seeded {count} consultations (from treatments.csv).")


def seed_sample_allergies_and_medications():
    """A few illustrative EHR entries so the demo isn't empty on first login."""
    patients = Patient.query.order_by(Patient.id).limit(10).all()
    count_a, count_m = 0, 0
    sample_allergies = [("Penicillin", "Rash"), ("Peanuts", "Swelling"), ("Dust", "Sneezing")]
    sample_meds = [("Paracetamol", "500 mg", "Twice a day"), ("Vitamin D3", "60,000 IU", "Once a week")]

    for i, patient in enumerate(patients):
        if not Allergy.query.filter_by(patient_id=patient.id).first() and i % 3 == 0:
            allergen, reaction = sample_allergies[i % len(sample_allergies)]
            db.session.add(Allergy(patient_id=patient.id, allergen=allergen, reaction=reaction))
            count_a += 1
        if not Medication.query.filter_by(patient_id=patient.id).first() and i % 2 == 0:
            name, dosage, freq = sample_meds[i % len(sample_meds)]
            db.session.add(Medication(patient_id=patient.id, medicine_name=name, dosage=dosage, frequency=freq))
            count_m += 1
    db.session.commit()
    print(f"Seeded {count_a} sample allergies and {count_m} sample medications.")


def seed_sample_medical_background():
    """A few illustrative Past Illness / Surgery / Family History rows
    (Milestone 2 Day 5) so the Medical History page isn't empty."""
    patients = Patient.query.order_by(Patient.id).limit(10).all()
    count_i, count_s, count_f = 0, 0, 0
    sample_illnesses = [("Dengue Fever", "2018"), ("Typhoid", "2016"), ("Viral Fever", "2014")]
    sample_surgeries = [("Appendectomy", date(2017, 3, 20)), ("Tonsillectomy", date(2015, 6, 10))]
    sample_family = [("Diabetes Mellitus", "Father"), ("Hypertension", "Mother"), ("Asthma", "Sister")]

    for i, patient in enumerate(patients):
        if not PastIllness.query.filter_by(patient_id=patient.id).first() and i % 3 == 0:
            illness, year = sample_illnesses[i % len(sample_illnesses)]
            db.session.add(PastIllness(patient_id=patient.id, illness=illness, year=year))
            count_i += 1
        if not PastSurgery.query.filter_by(patient_id=patient.id).first() and i % 4 == 0:
            surgery, sdate = sample_surgeries[i % len(sample_surgeries)]
            db.session.add(PastSurgery(patient_id=patient.id, surgery=surgery, surgery_date=sdate))
            count_s += 1
        if not FamilyHistory.query.filter_by(patient_id=patient.id).first() and i % 2 == 0:
            condition, relation = sample_family[i % len(sample_family)]
            db.session.add(FamilyHistory(patient_id=patient.id, condition=condition, relation=relation))
            count_f += 1
    db.session.commit()
    print(f"Seeded {count_i} past illnesses, {count_s} past surgeries, {count_f} family history rows.")


def seed_aadhaar_numbers():
    """Give a few patients a sample Aadhaar number so Patient Search (Day 1) has something to find."""
    patients = Patient.query.order_by(Patient.id).limit(15).all()
    count = 0
    for i, patient in enumerate(patients):
        if not patient.aadhaar_number:
            patient.aadhaar_number = f"{2000 + i:04d} {1000 + i:04d} {5000 + i:04d}"
            count += 1
    db.session.commit()
    print(f"Assigned Aadhaar numbers to {count} patients.")


def seed_medicines():
    """Milestone 3 Day 2 — a small pharmacy inventory to demo with."""
    if Medicine.query.count() > 0:
        print("Medicines already seeded, skipping.")
        return
    sample_medicines = [
        ("Paracetamol 500 mg", "Tablet", "ABC Pharma Ltd.", 250, 15.00, date(2027, 12, 31)),
        ("Amoxicillin 250 mg", "Capsule", "XYZ Pharmaceuticals", 120, 45.00, date(2027, 8, 15)),
        ("Cough Syrup", "Syrup", "HealthCare Pvt. Ltd.", 45, 80.00, date(2026, 10, 20)),
        ("Ibuprofen 400 mg", "Tablet", "LifeCare Pharma", 300, 20.00, date(2027, 5, 10)),
        ("Vitamin D3 60,000 IU", "Tablet", "Wellness Pharma", 75, 30.00, date(2027, 3, 5)),
        ("Cetirizine 10 mg", "Tablet", "ABC Pharma Ltd.", 200, 10.00, date(2027, 11, 1)),
        ("ORS Sachet", "Syrup", "HealthCare Pvt. Ltd.", 150, 25.00, date(2027, 6, 30)),
        ("Azithromycin 500 mg", "Tablet", "XYZ Pharmaceuticals", 18, 55.00, date(2026, 9, 15)),
        ("Metformin 500 mg", "Tablet", "LifeCare Pharma", 90, 18.00, date(2027, 1, 20)),
        ("Insulin Injection", "Injection", "Wellness Pharma", 12, 350.00, date(2026, 8, 1)),
    ]
    for name, category, manufacturer, stock, price, expiry in sample_medicines:
        db.session.add(Medicine(name=name, category=category, manufacturer=manufacturer,
                                 stock=stock, unit_price=price, expiry_date=expiry))
    db.session.commit()
    print(f"Seeded {len(sample_medicines)} medicines.")


def seed_sample_billing():
    """Milestone 3 Day 3 — a couple of paid invoices so Billing History isn't empty."""
    if Bill.query.count() > 0:
        print("Bills already seeded, skipping.")
        return
    patients = Patient.query.order_by(Patient.id).limit(5).all()
    count = 0
    for patient in patients:
        consultation = patient.consultations[0] if patient.consultations else None
        sub_total = 500.00
        bill = Bill(patient_id=patient.id, bill_date=date.today(), sub_total=sub_total,
                     discount=0, tax=0, total_amount=sub_total,
                     payment_method="UPI", payment_status="Paid",
                     transaction_id=f"UPI{1000000000 + patient.id}")
        db.session.add(bill)
        db.session.flush()
        db.session.add(BillItem(
            bill_id=bill.id, service_type="Consultation",
            description=f"Consultation with Dr. {consultation.doctor.full_name}" if consultation else "General Consultation",
            reference_id=f"CONS{consultation.id:04d}" if consultation else f"CONS{bill.id:04d}",
            amount=sub_total,
        ))
        count += 1
    db.session.commit()
    print(f"Seeded {count} sample bills.")


def seed_sample_notifications():
    """Milestone 3 Day 5 — a few notification rows so the dashboard isn't empty."""
    if Notification.query.count() > 0:
        print("Notifications already seeded, skipping.")
        return
    patients = Patient.query.order_by(Patient.id).limit(6).all()
    templates = [
        ("Appointment Reminder", "Your appointment is scheduled soon. Please arrive 15 minutes early.", "Delivered"),
        ("Lab Report", "Your lab report is available. Please check.", "Delivered"),
        ("Prescription Ready", "Your prescription is ready for collection at the pharmacy.", "Read"),
        ("Billing Reminder", "Your payment is pending. Please make the payment at your earliest convenience.", "Delivered"),
        ("General Info", "Free health check-up camp this weekend at City Care Hospital.", "Failed"),
    ]
    count = 0
    for i, patient in enumerate(patients):
        notif_type, message, status = templates[i % len(templates)]
        db.session.add(Notification(patient_id=patient.id, notif_type=notif_type,
                                     message=message, delivery_method="In-App", status=status))
        count += 1
    db.session.commit()
    print(f"Seeded {count} sample notifications.")


def seed_sample_feedback():
    """Milestone 4 Day 6 — a few feedback entries so the Feedback page and
    average satisfaction score aren't empty on first login."""
    if Feedback.query.count() > 0:
        print("Feedback already seeded, skipping.")
        return
    patients = Patient.query.order_by(Patient.id).limit(6).all()
    doctors = Doctor.query.order_by(Doctor.id).all()
    sample_comments = [
        "Doctor was very attentive and explained everything clearly.",
        "Waiting time was a bit long, but staff were helpful.",
        "Great experience overall, will recommend to others.",
        "Lab results were delivered quickly.",
        "Pharmacy staff were courteous and efficient.",
        "Very satisfied with the consultation and follow-up.",
    ]
    count = 0
    for i, patient in enumerate(patients):
        if not doctors:
            break
        doctor = doctors[i % len(doctors)]
        db.session.add(Feedback(
            patient_id=patient.id, doctor_id=doctor.id,
            rating_doctor=4 + (i % 2), rating_hospital=3 + (i % 3),
            rating_lab=4, rating_pharmacy=4 + (i % 2),
            comments=sample_comments[i % len(sample_comments)],
        ))
        count += 1
    db.session.commit()
    print(f"Seeded {count} sample feedback entries.")


def seed_sample_activity_log():
    """Milestone 4 Day 1/3 — a few historical activity rows so 'Recent
    System Activity' has something to show before the app has been used live."""
    if ActivityLog.query.count() > 0:
        print("Activity log already seeded, skipping.")
        return
    admin = User.query.filter_by(role="admin").first()
    sample_events = [
        ("System Initialized", "Integrated Patient Care Management System started successfully.", "info"),
        ("Database Seeded", "Sample dataset loaded for demo purposes.", "info"),
    ]
    count = 0
    for action, desc, icon in sample_events:
        db.session.add(ActivityLog(action=action, description=desc,
                                    user_id=admin.id if admin else None, icon=icon))
        count += 1
    db.session.commit()
    print(f"Seeded {count} activity log entries (more will appear as you use the app).")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()  # safety net in case tables don't exist yet
        create_default_logins()
        seed_doctors()
        seed_patients()
        seed_appointments()
        seed_consultations_from_treatments()
        seed_sample_allergies_and_medications()
        seed_sample_medical_background()
        seed_aadhaar_numbers()
        seed_medicines()
        seed_sample_billing()
        seed_sample_notifications()
        seed_sample_feedback()
        seed_sample_activity_log()
        print("\nSeeding complete! You can now log in with any of the default accounts.")
