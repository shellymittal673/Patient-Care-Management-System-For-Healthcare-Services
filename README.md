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



## 5. Run the app

```
python app.py
```

Open your browser to: **http://127.0.0.1:5000**



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





