from datetime import datetime
from app import db


class GameMatch(db.Model):
    __tablename__ = "game_matches"

    id = db.Column(db.Integer, primary_key=True)

    # Players
    player1_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Decks used
    player1_deck_id = db.Column(db.Integer, db.ForeignKey("decks.id"), nullable=False)
    player2_deck_id = db.Column(db.Integer, db.ForeignKey("decks.id"), nullable=True)

    # Match status: waiting, active, completed, abandoned
    status = db.Column(db.String(20), nullable=False, default="waiting")

    # Winner tracking
    winner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    win_condition = db.Column(db.String(50))

    # Timing
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    player1 = db.relationship("User", foreign_keys=[player1_id], backref="matches_as_p1")
    player2 = db.relationship("User", foreign_keys=[player2_id], backref="matches_as_p2")
    player1_deck = db.relationship("Deck", foreign_keys=[player1_deck_id])
    player2_deck = db.relationship("Deck", foreign_keys=[player2_deck_id])
    winner = db.relationship("User", foreign_keys=[winner_id])
