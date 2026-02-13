"""Seed card data - Run with: py -m flask shell, then exec(open('migrations/seed_cards.py').read())"""
from app import db
from app.models import Card

strategy_cards = [
    {"name": "Push Hard", "card_type": "strategy", "stats": {"speed_modifier": 3, "engine_wear": 2}, "description": "+3 Speed, +2 Engine Wear"},
    {"name": "Balanced Pace", "card_type": "strategy", "stats": {"speed_modifier": 2, "engine_wear": 1}, "description": "+2 Speed, +1 Engine Wear"},
    {"name": "Smooth Sector", "card_type": "strategy", "stats": {"speed_modifier": 2, "engine_wear": -1}, "description": "+2 Speed, -1 Engine Wear if no tactics"},
]

tactics_cards = [
    {"name": "Engine Protect", "card_type": "tactics", "stats": {"effect_type": "reduce_engine_wear", "wear_reduction": 1}, "description": "Reduce Engine Wear by 1"},
    {"name": "Dirty Air", "card_type": "tactics", "stats": {"effect_type": "opponent_speed_reduction", "speed_reduction": 1}, "description": "Opponent -1 Speed"},
]

event_cards = [
    {"name": "Safety Car", "card_type": "event", "stats": {"effect_type": "all_players", "forced_speed": 2}, "description": "All players speed = 2"},
]

all_cards = strategy_cards + tactics_cards + event_cards
print(f"Seeding {len(all_cards)} cards...")
for card_data in all_cards:
    if not Card.query.filter_by(name=card_data["name"]).first():
        db.session.add(Card(**card_data))
        print(f"  Created {card_data['name']}")
db.session.commit()
print(f"✓ Seeded {len(all_cards)} cards")
