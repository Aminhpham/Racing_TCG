from app import db
from sqlalchemy.dialects.postgresql import JSON


class Card(db.Model):
    __tablename__ = "cards"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    card_type = db.Column(db.String(20), nullable=False)  # strategy, tactics, event
    image_url = db.Column(db.String(255))
    stats = db.Column(JSON)  # card-specific attributes (speed_modifier, engine_wear, effect_type, etc.)
    description = db.Column(db.Text)
    requirements = db.Column(JSON)  # play conditions (min_resources, requires_leader, etc.)
