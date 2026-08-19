from flask import Blueprint, render_template
from flask_login import login_required, current_user

api_dashboard_bp = Blueprint("api_dashboard", __name__, url_prefix="/api-management")

ENDPOINTS = [
    {"name": "Patient API",      "path": "/api/patients",      "methods": "GET, POST"},
    {"name": "Doctor API",       "path": "/api/doctors",       "methods": "GET, POST"},
    {"name": "Consultation API", "path": "/api/consultations", "methods": "GET"},
    {"name": "Prescription API", "path": "/api/prescriptions", "methods": "GET"},
    {"name": "Laboratory API",   "path": "/api/laboratory",    "methods": "GET"},
    {"name": "Billing API",      "path": "/api/billing",       "methods": "GET"},
    {"name": "Notification API", "path": "/api/notifications", "methods": "GET, POST"},
]


@api_dashboard_bp.route("/")
@login_required
def dashboard():
    return render_template("api_dashboard.html", endpoints=ENDPOINTS)
