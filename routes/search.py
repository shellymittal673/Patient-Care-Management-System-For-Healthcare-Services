from flask import Blueprint, render_template, request
from flask_login import login_required

from models.patient import Patient

search_bp = Blueprint("search", __name__, url_prefix="/search")


@search_bp.route("/")
@login_required
def patient_search():
    search_by = request.args.get("search_by", "")
    query = request.args.get("query", "").strip()
    results = []
    searched = bool(query)

    if query:
        q = Patient.query
        if search_by == "id":
            # accept raw id or PAT0001-style codes
            digits = "".join(ch for ch in query if ch.isdigit())
            if digits:
                results = q.filter(Patient.id == int(digits)).all()
        elif search_by == "phone":
            results = q.filter(Patient.contact_number.ilike(f"%{query}%")).all()
        elif search_by == "aadhaar":
            results = q.filter(Patient.aadhaar_number.ilike(f"%{query}%")).all()
        elif search_by == "email":
            results = q.filter(Patient.email.ilike(f"%{query}%")).all()
        else:  # name (default)
            results = q.filter(Patient.full_name.ilike(f"%{query}%")).all()

    return render_template(
        "patient_search.html",
        results=results, searched=searched, search_by=search_by or "name", query=query,
    )
