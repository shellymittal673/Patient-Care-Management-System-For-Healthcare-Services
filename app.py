import time
from datetime import datetime
from flask import Flask, redirect, url_for, request, g
from flask_login import LoginManager

from config import Config
from models import db
from models.user import User

APP_START_TIME = datetime.utcnow()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # ---- Flask-Login setup ----
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ---- Milestone 4: real request timing for the Performance dashboard ----
    @app.before_request
    def _start_timer():
        g._request_start = time.time()

    @app.after_request
    def _log_request(response):
        # Skip static files and the tiny polling-style routes so the log
        # stays meaningful, not flooded with asset requests.
        if request.endpoint and not request.endpoint.startswith("static"):
            try:
                from models.request_log import RequestLog
                elapsed_ms = int((time.time() - getattr(g, "_request_start", time.time())) * 1000)
                blueprint = request.endpoint.split(".")[0] if "." in request.endpoint else None
                db.session.add(RequestLog(
                    endpoint=request.endpoint, blueprint=blueprint, method=request.method,
                    status_code=response.status_code, response_time_ms=elapsed_ms,
                ))
                db.session.commit()
            except Exception:
                db.session.rollback()
        return response

    # ---- Register blueprints ----
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.patients import patients_bp
    from routes.doctors import doctors_bp
    from routes.appointments import appointments_bp
    from routes.ehr import ehr_bp
    from routes.consultations import consultations_bp
    from routes.prescriptions import prescriptions_bp
    from routes.lab import lab_bp
    from routes.medical_history import medical_history_bp
    from routes.search import search_bp
    from routes.pharmacy import pharmacy_bp
    from routes.billing import billing_bp
    from routes.api import api_bp
    from routes.api_dashboard import api_dashboard_bp
    from routes.notifications import notifications_bp
    from routes.feedback import feedback_bp
    from routes.reports_extra import reports_extra_bp
    from routes.system_integration import system_integration_bp
    from routes.performance import performance_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(doctors_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(ehr_bp)
    app.register_blueprint(consultations_bp)
    app.register_blueprint(prescriptions_bp)
    app.register_blueprint(lab_bp)
    app.register_blueprint(medical_history_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(pharmacy_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(api_dashboard_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(reports_extra_bp)
    app.register_blueprint(system_integration_bp)
    app.register_blueprint(performance_bp)

    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
