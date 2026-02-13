"""Seed car data for the Racing TCG

Run this script with:
    py -m flask shell
    >>> exec(open('migrations/seed_cars.py').read())
"""

from app import db
from app.models import Card

# Car data (stored as special cards with card_type="car")
cars = [
    {
        "name": "Vanilla Car",
        "card_type": "car",
        "stats": {
            "engine": 8,
            "tires": 6,
            "fuel": 6,
            "reliability": 3,
            "ability": ""
        },
        "description": "Baseline car with balanced stats"
    },
    {
        "name": "Red Car",
        "card_type": "car",
        "stats": {
            "engine": 8,
            "tires": 5,
            "fuel": 6,
            "reliability": 4,
            "ability": "+1 Speed on Tactics cards"
        },
        "description": "Aggressive car with bonus speed on tactics"
    },
    {
        "name": "Blue Car",
        "card_type": "car",
        "stats": {
            "engine": 9,
            "tires": 6,
            "fuel": 5,
            "reliability": 2,
            "ability": "–1 Speed on aggressive strategies"
        },
        "description": "High engine but penalized on aggressive plays"
    },
    {
        "name": "Yellow Car",
        "card_type": "car",
        "stats": {
            "engine": 8,
            "tires": 6,
            "fuel": 6,
            "reliability": 3,
            "ability": "First Reliability Check auto-passes"
        },
        "description": "Reliable car that auto-passes first reliability check"
    },
    {
        "name": "Green Car",
        "card_type": "car",
        "stats": {
            "engine": 8,
            "tires": 6,
            "fuel": 6,
            "reliability": 3,
            "ability": "Reliability modifiers based on stat type"
        },
        "description": "Modified reliability checks based on which stat triggered it"
    }
]

print("Seeding car data...")

for car_data in cars:
    existing = Card.query.filter_by(name=car_data["name"], card_type="car").first()
    if existing:
        print(f"  Skipping {car_data['name']} (already exists)")
        continue

    car = Card(**car_data)
    db.session.add(car)
    print(f"  Created {car_data['name']}")

db.session.commit()
print(f"✓ Seeded {len(cars)} cars")
