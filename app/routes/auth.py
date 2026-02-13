from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Deck, Card

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def create_starter_decks_for_new_user(user_id):
    """Create 4 starter decks for a newly registered user"""
    # Get cards by type
    cars = Card.query.filter_by(card_type='car').all()
    strategies = Card.query.filter_by(card_type='strategy').all()
    tactics = Card.query.filter_by(card_type='tactics').all()
    events = Card.query.filter_by(card_type='event').all()

    if len(cars) < 1 or len(strategies) < 10 or len(tactics) < 10:
        return  # Not enough cards, skip starter deck creation

    # Starter Deck 1: Aggressive Racer
    deck1 = Deck(
        user_id=user_id,
        name="Starter: Aggressive Racer",
        description="High-speed aggressive deck focused on maximum speed",
        card_ids=[cars[1].id] + [s.id for s in strategies[:7]] + [t.id for t in tactics[:7]] + [e.id for e in events[:3]]
    )
    while len(deck1.card_ids) < 40:
        deck1.card_ids.append(strategies[len(deck1.card_ids) % len(strategies)].id)
    deck1.card_ids = deck1.card_ids[:40]

    # Starter Deck 2: Balanced Racer
    deck2 = Deck(
        user_id=user_id,
        name="Starter: Balanced Racer",
        description="Well-rounded deck with balanced strategy",
        card_ids=[cars[0].id] + [s.id for s in strategies[5:12]] + [t.id for t in tactics[5:12]] + [e.id for e in events[:3]]
    )
    while len(deck2.card_ids) < 40:
        deck2.card_ids.append(strategies[len(deck2.card_ids) % len(strategies)].id)
    deck2.card_ids = deck2.card_ids[:40]

    # Starter Deck 3: Defensive Racer
    deck3 = Deck(
        user_id=user_id,
        name="Starter: Defensive Racer",
        description="Conservative deck focused on reliability and endurance",
        card_ids=[cars[3].id] + [s.id for s in strategies[8:]] + [t.id for t in tactics[8:]] + [e.id for e in events[:4]]
    )
    while len(deck3.card_ids) < 40:
        deck3.card_ids.append(tactics[len(deck3.card_ids) % len(tactics)].id)
    deck3.card_ids = deck3.card_ids[:40]

    # Starter Deck 4: Mixed Strategy
    deck4 = Deck(
        user_id=user_id,
        name="Starter: Mixed Strategy",
        description="Versatile deck with mix of all card types",
        card_ids=[cars[2].id] + [s.id for s in strategies[::2][:8]] + [t.id for t in tactics[::2][:8]] + [e.id for e in events[:4]]
    )
    while len(deck4.card_ids) < 40:
        deck4.card_ids.append(strategies[len(deck4.card_ids) % len(strategies)].id)
    deck4.card_ids = deck4.card_ids[:40]

    # Add all decks
    db.session.add(deck1)
    db.session.add(deck2)
    db.session.add(deck3)
    db.session.add(deck4)


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

        # Create starter decks for new user
        create_starter_decks_for_new_user(user.id)
        db.session.commit()

        flash("Account created successfully with 4 starter decks! Please log in.", "success")
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
