from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import JSON


class GameState(db.Model):
    __tablename__ = "game_states"

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey("game_matches.id"), nullable=False, unique=True)

    # Current game phase: strategy_selection, strategy_reveal, react, speed_calculation, game_over
    current_phase = db.Column(db.String(20), nullable=False)

    current_turn = db.Column(db.Integer, default=1)
    active_player_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    # Complete game state as JSON
    state_data = db.Column(JSON, nullable=False)
    # Structure:
    # {
    #   "player1": {
    #     "car_stats": {"engine": 0, "tires": 0, "fuel": 0, "reliability": 0},
    #     "position": {"lap": 1, "progress": 0, "is_leader": True},
    #     "hand": [card_id, ...],
    #     "deck": [card_id, ...],
    #     "discard": [card_id, ...],
    #     "resources": 5,
    #     "selected_strategy": null,
    #     "played_tactics": [],
    #     "wear_accumulated": 0
    #   },
    #   "player2": { ... },
    #   "turn_history": [...]
    # }

    # Last update timestamp
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    match = db.relationship("GameMatch", backref="game_state", uselist=False)
