"""Seed car data for the Racing TCG

Run this script with:
    py -m flask shell
    >>> exec(open('migrations/seed_cars.py').read())
"""

from app import db
from app.models import Card

# Car data (stored as special cards with card_type="car")
# Each car has a base_speed (1-6) and reliability threshold for dice rolls
# Higher reliability = harder to move (need higher dice roll)
cars = [
    {
        "name": "Lightning Bolt",
        "card_type": "car",
        "stats": {
            "base_speed": 6,
            "engine": 8,
            "tires": 6,
            "fuel": 5,
            "reliability": 6,
            "ability": "When successful roll: +1 bonus speed"
        },
        "description": "Speed Demon - Fastest but only moves on roll of 6 (16%)"
    },
    {
        "name": "Speedster",
        "card_type": "car",
        "stats": {
            "base_speed": 5,
            "engine": 8,
            "tires": 5,
            "fuel": 6,
            "reliability": 5,
            "ability": "Aggressive style with high risk"
        },
        "description": "Aggressive - Fast but risky, moves on roll 5+ (33%)"
    },
    {
        "name": "All-Rounder",
        "card_type": "car",
        "stats": {
            "base_speed": 4,
            "engine": 7,
            "tires": 6,
            "fuel": 6,
            "reliability": 4,
            "ability": "Balanced performance"
        },
        "description": "Balanced - Standard speed and reliability, moves on 4+ (50%)"
    },
    {
        "name": "The Tank",
        "card_type": "car",
        "stats": {
            "base_speed": 3,
            "engine": 6,
            "tires": 7,
            "fuel": 8,
            "reliability": 3,
            "ability": "Consistent movement, slow but steady"
        },
        "description": "Reliable Racer - Slow but consistent, moves on 3+ (66%)"
    },
    {
        "name": "Tortoise",
        "card_type": "car",
        "stats": {
            "base_speed": 2,
            "engine": 6,
            "tires": 8,
            "fuel": 8,
            "reliability": 2,
            "ability": "Almost always moves, very reliable"
        },
        "description": "Ultra-Reliable - Very slow but almost always moves on 2+ (83%)"
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
