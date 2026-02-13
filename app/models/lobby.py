from datetime import datetime
from app import db


class Lobby(db.Model):
    __tablename__ = "lobbies"

    id = db.Column(db.Integer, primary_key=True)
    host_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    host_deck_id = db.Column(db.Integer, db.ForeignKey("decks.id"), nullable=False)

    name = db.Column(db.String(100), nullable=False)
    is_private = db.Column(db.Boolean, default=False)
    password = db.Column(db.String(64), nullable=True)

    # Status: open, full, in_progress
    status = db.Column(db.String(20), default="open")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    host = db.relationship("User", backref="hosted_lobbies")
    host_deck = db.relationship("Deck")
