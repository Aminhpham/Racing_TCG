from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Card

cards_bp = Blueprint("cards", __name__, url_prefix="/cards")

@cards_bp.route("/")
@login_required
def index():
    # Get all cards, grouped by type
    strategy_cards = Card.query.filter_by(card_type='strategy').all()
    tactics_cards = Card.query.filter_by(card_type='tactics').all()
    event_cards = Card.query.filter_by(card_type='event').all()
    car_cards = Card.query.filter_by(card_type='car').all()

    return render_template('cards/index.html',
                         strategy_cards=strategy_cards,
                         tactics_cards=tactics_cards,
                         event_cards=event_cards,
                         car_cards=car_cards)
