from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy.orm.attributes import flag_modified
from app import db
from app.models import Deck, Card

decks_bp = Blueprint("decks", __name__, url_prefix="/decks")

@decks_bp.route("/")
@login_required
def index():
    decks = Deck.query.filter_by(user_id=current_user.id).all()
    return render_template('decks/index.html', decks=decks)

@decks_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description", "")

        deck = Deck(
            user_id=current_user.id,
            name=name,
            description=description,
            card_ids=[]
        )
        db.session.add(deck)
        db.session.commit()

        flash("Deck created successfully! Now add some cards.", "success")
        return redirect(url_for('decks.edit', deck_id=deck.id))

    return render_template('decks/create.html')

@decks_bp.route("/<int:deck_id>")
@login_required
def view(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        flash("You don't have permission to view this deck.")
        return redirect(url_for('decks.index'))

    cards = Card.query.filter(Card.id.in_(deck.card_ids)).all() if deck.card_ids else []
    return render_template('decks/view.html', deck=deck, cards=cards)

@decks_bp.route("/<int:deck_id>/edit")
@login_required
def edit(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        flash("You don't have permission to edit this deck.")
        return redirect(url_for('decks.index'))

    # Get all available cards
    all_cards = Card.query.all()

    # Get cards already in deck
    deck_cards = Card.query.filter(Card.id.in_(deck.card_ids)).all() if deck.card_ids else []

    return render_template('decks/edit.html', deck=deck, all_cards=all_cards, deck_cards=deck_cards)

@decks_bp.route("/<int:deck_id>/add_card/<int:card_id>", methods=["POST"])
@login_required
def add_card(deck_id, card_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        return jsonify({"success": False, "error": "Permission denied"}), 403

    # Check if card exists
    card = Card.query.get_or_404(card_id)

    # Initialize card_ids if None
    if deck.card_ids is None:
        deck.card_ids = []

    # Check deck limit (40 cards)
    if len(deck.card_ids) >= 40:
        return jsonify({"success": False, "error": "Deck is full (40 cards max)"}), 400

    # Add card to deck
    if card_id not in deck.card_ids:
        deck.card_ids.append(card_id)
        flag_modified(deck, 'card_ids')  # Tell SQLAlchemy the field changed
        db.session.commit()
        return jsonify({"success": True, "card_count": len(deck.card_ids)})
    else:
        return jsonify({"success": False, "error": "Card already in deck"}), 400

@decks_bp.route("/<int:deck_id>/remove_card/<int:card_id>", methods=["POST"])
@login_required
def remove_card(deck_id, card_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        return jsonify({"success": False, "error": "Permission denied"}), 403

    # Initialize card_ids if None
    if deck.card_ids is None:
        deck.card_ids = []

    # Remove card from deck
    if card_id in deck.card_ids:
        deck.card_ids.remove(card_id)
        flag_modified(deck, 'card_ids')  # Tell SQLAlchemy the field changed
        db.session.commit()
        return jsonify({"success": True, "card_count": len(deck.card_ids)})
    else:
        return jsonify({"success": False, "error": "Card not in deck"}), 400

@decks_bp.route("/<int:deck_id>/delete", methods=["POST"])
@login_required
def delete(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    if deck.user_id != current_user.id:
        flash("You don't have permission to delete this deck.", "error")
        return redirect(url_for('decks.index'))

    deck_name = deck.name
    db.session.delete(deck)
    db.session.commit()

    flash(f"Deck '{deck_name}' has been deleted.", "success")
    return redirect(url_for('decks.index'))
