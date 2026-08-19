from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from models import db
from models.user import User
from models.patient import Patient
from models.doctor import Doctor
from models.activity_log import log_activity

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone_number = request.form.get("phone_number", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        role = request.form.get("role", "patient")

        # ---- basic validation ----
        if not full_name or not email or not password:
            flash("Full name, email, and password are required.", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "error")
            return render_template("register.html")

        if role not in ("admin", "doctor", "nurse", "patient", "pharmacist"):
            role = "patient"

        # ---- create the user ----
        user = User(full_name=full_name, email=email, phone_number=phone_number, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # ---- auto-create a matching profile row ----
        if role == "patient":
            profile = Patient(user_id=user.id, full_name=full_name,
                               contact_number=phone_number, email=email)
            db.session.add(profile)
            db.session.commit()
        elif role == "doctor":
            profile = Doctor(user_id=user.id, full_name=full_name,
                              phone_number=phone_number, email=email)
            db.session.add(profile)
            db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role")  # which tab/card the person submitted from

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        if role and user.role != role:
            flash(f"That account is registered as '{user.role}', not '{role}'.", "error")
            return render_template("login.html")

        login_user(user)
        log_activity("User Login", f"{user.full_name} ({user.role}) logged in",
                      user_id=user.id, icon="login")
        db.session.commit()
        flash(f"Welcome back, {user.full_name}!", "success")
        return redirect(url_for("dashboard.home"))

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
