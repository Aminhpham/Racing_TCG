from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import ARRAY, Integer


class Deck(db.Model):
    __tablename__ = "decks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    card_ids = db.Column(ARRAY(Integer))  # list of card IDs
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
