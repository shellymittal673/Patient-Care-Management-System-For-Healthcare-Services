# Integrated Patient Care Management System

Flask + MySQL system with role-based login (Admin / Doctor / Nurse / Patient),
patient registration & profiles, doctor management, and appointment booking.

## 1. Install requirements

Open this folder in VS Code, open a terminal, then run:

```
pip install -r requirements.txt
```

## 2. Create the MySQL database

Open MySQL Workbench (or your MySQL client / terminal) and run:

```sql
CREATE DATABASE patient_care_db;
```

That's it — you don't need to run `database/schema.sql` by hand; Flask
creates the tables automatically the first time you seed the data (next step).

## 3. Set your MySQL credentials

Open `config.py` and update these lines with your actual MySQL username/password:

```python
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")     # <-- put your MySQL password here
```

If you're using XAMPP/default MySQL install, username is usually `root` and
password is often blank (`""`).

## 4. Seed the database

This creates the tables AND loads your dataset (patients, doctors,
appointments) plus 4 default login accounts:

```
python seed_data.py
```

You should see output like:
```
Default login accounts created (admin/doctor/nurse/patient/pharmacist @pcms.com).
Seeded 10 doctors.
Seeded 39 patients.
Seeded 160 appointments.
Seeded 160 consultations (from treatments.csv).
Seeded 4 sample allergies and 5 sample medications.
Seeded 4 past illnesses, 3 past surgeries, 5 family history rows.
Assigned Aadhaar numbers to 15 patients.
Seeded 10 medicines.
Seeded 5 sample bills.
Seeded 6 sample notifications.

Seeding complete!
```

## 5. Run the app

```
python app.py
```

Open your browser to: **http://127.0.0.1:5000**

## Default login accounts (created by the seed script)

| Role       | Email                | Password    |
|------------|----------------------|-------------|
| Admin      | admin@pcms.com       | admin123    |
| Doctor     | doctor@pcms.com      | doctor123   |
| Nurse      | nurse@pcms.com       | nurse123    |
| Patient    | patient@pcms.com     | patient123  |
| Pharmacist | pharmacist@pcms.com  | pharma123   |

You can also register brand-new accounts from the Login page → "Register here".

## Project structure

```
Integrated_Patient_Care/
├── app.py                  # Flask app factory + entry point
├── config.py                # MySQL connection settings
├── seed_data.py              # Loads dataset CSVs + default accounts
├── requirements.txt
├── models/                   # SQLAlchemy models (User, Patient, Doctor, Appointment, MedicalRecord)
├── routes/                   # Blueprints (auth, dashboard, patients, doctors, appointments)
├── templates/                # Jinja2 HTML templates
├── static/css/style.css      # Styling
└── database/
    ├── schema.sql             # Reference SQL (optional — for inspection only)
    ├── patients.csv            # Original dataset
    ├── doctors.csv
    ├── appointments.csv
    ├── treatments.csv
    └── billing.csv
```

## What's implemented (Milestone 1)

- **Day 1–2**: Role-based authentication (Admin/Doctor/Nurse/Patient) with
  Flask-Login + password hashing (Werkzeug)
- **Day 3**: Patient registration form, patient list, patient profile view
  with edit/delete
- **Day 4**: Doctor management — add/edit/delete doctor profiles
- **Day 5**: Appointment booking, patient/doctor-scoped appointment views,
  status updates (Scheduled/Completed/Cancelled/No-show)
- **Day 6**: Role-specific dashboards (Admin stats, Doctor's appointment
  list, Nurse overview, Patient self-service view)

## What's implemented (Milestone 2) — builds directly on Milestone 1

- **Day 1 — EHR / Medical Records**: a tabbed record per patient (Medical
  Summary, Diagnosis History, Allergies, Medications, Lab Reports, Documents)
  reachable from the existing Patient List / Patient Profile via a "View EHR"
  button — same `patients` table from Milestone 1, extended with height,
  weight, BMI (auto-calculated), smoking/alcohol status, and chronic diseases.
- **Day 2 — Consultation Management**: doctors record a visit (symptoms,
  diagnosis, treatment) against an existing patient + doctor pair from
  Milestone 1. Every consultation immediately shows up in that patient's EHR
  "Diagnosis History" tab — this is the direct connection between the two
  milestones.
- **Day 3 — Prescription Management**: create a prescription with multiple
  medicines (dynamic add/remove rows), live-updating preview pane, and a
  printable prescription view — linked to the same patient/doctor records.
- **Day 4 — Laboratory Management**: request a lab test for a patient, track
  status (Pending/In Progress/Completed), and upload a real result file
  (PDF/image) which becomes viewable from both the Lab dashboard and the
  patient's EHR "Lab Reports" tab.
- **Day 5 — Patient Medical History**: rather than a separate page, the EHR
  view itself acts as the aggregated medical history — pulling together
  consultations, allergies, medications, and lab reports for one patient in
  one place, which is what Milestone 2 Day 5 asks for.

## What's implemented (Milestone 3) — builds on Milestone 1 + 2

- **Day 1 — Patient Search**: search by Patient ID, Name, Phone Number,
  Aadhaar Number, or Email — reuses the same `patients` table from
  Milestone 1, just adds an `aadhaar_number` column and a search form.
- **Day 2 — Pharmacy Management**: a new **Pharmacist** role and login,
  medicine inventory (add/update stock/delete), and a Dispense Medicine
  form that deducts real stock and logs who dispensed what to which patient.
- **Day 3 — Billing & Payment**: pick a patient, and the system automatically
  pulls their *unbilled* consultations, lab tests, and dispensed medicines as
  line items (so nothing gets billed twice) — check the ones to include, add
  discount/tax, choose a payment method, and it generates a real printable
  invoice.
- **Day 4 — REST API Management**: real JSON endpoints (`/api/patients`,
  `/api/doctors`, `/api/consultations`, `/api/prescriptions`,
  `/api/laboratory`, `/api/billing`, `/api/notifications`) plus a live API
  testing dashboard — the "Send Request" button and response-time chart
  measure actual `fetch()` calls against your running server, not fake
  numbers.
- **Day 5 — Notification Management**: notifications tied to real patients;
  "Refresh" scans actual upcoming appointments and completed lab results and
  generates reminders from them, so the notification list reflects what's
  really happening in the system.
- **Day 6 — Dashboard Analytics & Security**: builds on the Milestone 1
  Admin dashboard (charts, stats) — role-based access continues via the
  `roles_required` decorator, now covering 5 roles including Pharmacist.
- **Day 7 — System Integration**: every Milestone 3 module links back into
  Milestone 1/2 data (billing pulls from consultations/lab/pharmacy;
  pharmacy dispensing reduces real stock; notifications reference real
  patients) rather than existing as disconnected demo pages.

## What's implemented (Milestone 4) — final milestone, builds on 1 + 2 + 3

- **Day 1 — Analytics Dashboard**: the Admin dashboard now shows 6 real stat
  cards (Patients, Doctors, Today's Appointments, Completed Consultations,
  Cancelled Appointments, Pending Lab Reports), 4 live charts (Monthly Patient
  Registrations, Appointment Trends, Doctor-wise Consultation Count, Patient
  Demographics), a real Revenue Summary pulled from paid bills, and a genuine
  **Recent System Activity** feed — not placeholder text, an actual audit
  log (see Day 3 below).
- **Day 2 — Administrative Reporting**: a Reports hub with 7 report types
  (Patient, Appointment, Consultation, Prescription, Doctor Performance,
  Department-wise, Monthly Hospital) — each queries real data, and both
  **Export CSV** (a real file download) and **Print** work.
- **Day 3 — System Integration & Audit Trail**: every meaningful write
  action in the app (patient registered, appointment booked/cancelled,
  consultation completed, prescription generated, lab report uploaded,
  payment received, user login) writes a real row to an `activity_logs`
  table via a small `log_activity()` helper called from the relevant route.
  The System Integration page queries each module's table directly and times
  the query live, so "Connected" / record counts / response times are real,
  and the End-to-End Patient Workflow visual marks each step "Completed"
  only if that table actually has data.
- **Day 4/5 — Testing & Performance**: `app.py` has a `before_request` /
  `after_request` hook that times *every* request the server handles and
  logs it to a `request_logs` table. The Performance dashboard's Average
  Response Time, Error Rate, Uptime, and the Response Time Trend chart are
  all computed from that real log — browse a few pages, then reload the
  dashboard, and the numbers change.
- **Day 6 — Patient Feedback & Satisfaction**: patients rate Doctor,
  Hospital, Laboratory, and Pharmacy service (1-5 stars) with comments;
  Admin/Doctor see all submissions with filters by doctor/rating and a real
  average satisfaction score.
- **Day 7 — Final Integration**: the Reports & Search hub, System
  Integration overview, and Performance dashboard together give a live,
  data-driven picture of the whole system rather than a static summary
  screen.

**Note on scope**: some sub-items in the Milestone 4 brief (load testing
with simulated concurrent users, SQL-injection/XSS penetration testing,
Redis caching, cloud deployment) need infrastructure beyond a local Flask +
MySQL setup, so they aren't included here. Everything listed above is real,
working code you can demo live — nothing is mocked or hardcoded.

## Project structure

```
Integrated_Patient_Care/
├── app.py                  # Flask app factory + entry point
├── config.py                # MySQL connection settings
├── seed_data.py              # Loads dataset CSVs + default accounts + sample data (all 4 milestones)
├── requirements.txt
├── models/                   # SQLAlchemy models:
│                              #   User, Patient, Doctor, Appointment, MedicalRecord (Milestone 1)
│                              #   Allergy, Medication, Consultation, Prescription,
│                              #   PrescriptionItem, LabTest, PastIllness, PastSurgery,
│                              #   FamilyHistory (Milestone 2)
│                              #   Medicine, DispenseRecord, Bill, BillItem, Notification (Milestone 3)
│                              #   ActivityLog, Feedback, RequestLog (Milestone 4)
├── routes/                   # Blueprints:
│                              #   auth, dashboard, patients, doctors, appointments (Milestone 1)
│                              #   ehr, consultations, prescriptions, lab, medical_history (Milestone 2)
│                              #   search, pharmacy, billing, api, api_dashboard, notifications (Milestone 3)
│                              #   feedback, reports_extra, system_integration, performance (Milestone 4)
├── templates/                # Jinja2 HTML templates
├── static/
│   ├── css/style.css         # Styling
│   └── uploads/lab_reports/  # Uploaded lab report files land here
└── database/
    ├── schema.sql             # Reference SQL (optional — for inspection only)
    ├── patients.csv            # Original dataset
    ├── doctors.csv
    ├── appointments.csv
    ├── treatments.csv          # Now also seeds Consultation records (Milestone 2)
    └── billing.csv
```

## Updating an existing database (already ran Milestone 1/2 before)

Milestone 3 adds one new column to your **existing** `patients` table
(`aadhaar_number`), plus five brand-new tables (`medicines`,
`dispense_records`, `bills`, `bill_items`, `notifications`). New tables are
created automatically by `seed_data.py` — but since `patients` already
exists in your database, MySQL won't add the new column on its own. Run
this once in MySQL Workbench first:

```sql
USE patient_care_db;

ALTER TABLE patients
  ADD COLUMN aadhaar_number VARCHAR(20) NULL;
```

Then run `python seed_data.py` as usual — it will create the 5 new tables
and populate sample data for all of them.

If seeding fails with `Data truncated for column 'role'`, your `users`
table's `role` column was created before the Pharmacist role existed and
needs widening too:

```sql
ALTER TABLE users
  MODIFY COLUMN role ENUM('admin','doctor','nurse','patient','pharmacist') NOT NULL DEFAULT 'patient';
```

## Updating an existing database (already ran Milestone 1/2/3 before)

Milestone 4 adds three brand-new tables (`activity_logs`, `feedback`,
`request_logs`) but doesn't touch any existing table — no `ALTER TABLE`
needed this time. Just run:

```
python seed_data.py
```

and the new tables will be created automatically along with sample
feedback/activity data.

## Notes for your mentor demo

- All 4 roles have distinct dashboards and permissions (e.g. only Admin can
  delete records; Nurses can register patients but not doctors; Patients
  can't create consultations, prescriptions, or lab requests — try it and
  you'll get a 403).
- The database is pre-populated from a real Kaggle-style hospital dataset
  (patients.csv, doctors.csv, appointments.csv, treatments.csv) via
  `seed_data.py`, so you'll have realistic data — including consultations —
  to show immediately without manual entry.
- Passwords are hashed (never stored in plain text) — you can show this by
  checking the `users` table in MySQL Workbench.
- To show the Milestone 1 → Milestone 2 connection live: open any patient's
  profile (Milestone 1), click "View EHR" — you're now in Milestone 2, looking
  at the same patient record extended with medical data.
