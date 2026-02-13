from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import JSON


class GameLog(db.Model):
    __tablename__ = "game_logs"

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey("game_matches.id"), nullable=False)
    turn_number = db.Column(db.Integer, nullable=False)
    phase = db.Column(db.String(20), nullable=False)

    # Log entry
    # Event types: card_played, dice_roll, wear_applied, lap_completed, etc.
    event_type = db.Column(db.String(50), nullable=False)

    player_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    event_data = db.Column(JSON)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    match = db.relationship("GameMatch", backref="logs")
    player = db.relationship("User")
