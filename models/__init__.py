from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models so they register with SQLAlchemy metadata
from models.user import User          # noqa: E402,F401
from models.patient import Patient     # noqa: E402,F401
from models.doctor import Doctor       # noqa: E402,F401
from models.appointment import Appointment   # noqa: E402,F401
from models.medical_record import MedicalRecord  # noqa: E402,F401
from models.allergy import Allergy               # noqa: E402,F401
from models.medication import Medication         # noqa: E402,F401
from models.consultation import Consultation     # noqa: E402,F401
from models.prescription import Prescription, PrescriptionItem  # noqa: E402,F401
from models.lab_test import LabTest              # noqa: E402,F401
from models.medical_background import PastIllness, PastSurgery, FamilyHistory  # noqa: E402,F401
from models.medicine import Medicine, DispenseRecord    # noqa: E402,F401
from models.billing import Bill, BillItem               # noqa: E402,F401
from models.notification import Notification            # noqa: E402,F401
from models.activity_log import ActivityLog             # noqa: E402,F401
from models.feedback import Feedback                     # noqa: E402,F401
from models.request_log import RequestLog                # noqa: E402,F401
