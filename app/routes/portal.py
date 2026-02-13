from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

portal_bp = Blueprint("portal", __name__)

@portal_bp.route("/")
def root():
    """Root route - redirect to portal or login"""
    if current_user.is_authenticated:
        return redirect(url_for('portal.index'))
    return redirect(url_for('auth.login'))

@portal_bp.route("/portal")
@login_required
def index():
    return render_template("portal.html")
