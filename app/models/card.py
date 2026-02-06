from app import db
from sqlalchemy.dialects.postgresql import JSON


class Card(db.Model):
    __tablename__ = "cards"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255))
    stats = db.Column(JSON)  # attack, defense, cost, etc.
    description = db.Column(db.Text)
