from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# -------------------------
# REGISTER
# -------------------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username").strip()
        email = request.form.get("email").strip().lower()
        password = request.form.get("password")

        # Basic validation
        if not username or not email or not password:
            flash("All fields are required.")
            return redirect(url_for("auth.register"))

        # Check if user exists
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or email already exists.")
            return redirect(url_for("auth.register"))

        # Create user
        user = User(username=username, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully. Please log in.")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


# -------------------------
# LOGIN
# -------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email").strip().lower()
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            flash("Invalid email or password.")
            return redirect(url_for("auth.login"))

        login_user(user)
        flash("Logged in successfully.")
        return redirect(url_for("portal.index"))

    return render_template("auth/login.html")


# -------------------------
# LOGOUT
# -------------------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("auth.login"))
