"""
Seed script to populate the database with all game cards.
Run this with: python seed_all_cards.py
Use --force to skip confirmation: python seed_all_cards.py --force
"""

import sys
from app import create_app, db
from app.models import Card

app = create_app()

def seed_cars():
    """Seed the 5 car cards"""
    cars = [
        {
            "name": "Vanilla",
            "card_type": "car",
            "description": "Baseline car with balanced stats",
            "stats": {
                "engine": 8,
                "tires": 6,
                "fuel": 6,
                "reliability": 3,
                "ability": "Balanced performance"
            }
        },
        {
            "name": "Red Racer",
            "card_type": "car",
            "description": "High-speed aggressive racer",
            "stats": {
                "engine": 8,
                "tires": 5,
                "fuel": 6,
                "reliability": 4,
                "ability": "+1 Speed on Tactics cards"
            }
        },
        {
            "name": "Blue Speedster",
            "card_type": "car",
            "description": "Maximum speed, lower reliability",
            "stats": {
                "engine": 9,
                "tires": 6,
                "fuel": 5,
                "reliability": 2,
                "ability": "−1 Speed on aggressive strategies"
            }
        },
        {
            "name": "Yellow Thunder",
            "card_type": "car",
            "description": "Reliable and steady",
            "stats": {
                "engine": 8,
                "tires": 6,
                "fuel": 6,
                "reliability": 3,
                "ability": "First Reliability Check auto-passes"
            }
        },
        {
            "name": "Green Machine",
            "card_type": "car",
            "description": "Adaptable performance car",
            "stats": {
                "engine": 8,
                "tires": 6,
                "fuel": 6,
                "reliability": 3,
                "ability": "Reliability modifiers based on stat type"
            }
        }
    ]

    return cars

def seed_strategy_cards():
    """Seed strategy cards"""
    strategies = [
        {"name": "Push Hard", "description": "+3 Speed, Engine -2", "speed": 3, "engine": -2},
        {"name": "Aggressive Overtake", "description": "+4 Speed, Engine -3", "speed": 4, "engine": -3},
        {"name": "Risky Mapping", "description": "+5 Speed, Engine -4", "speed": 5, "engine": -4},
        {"name": "Full Send", "description": "+6 Speed, Engine -5", "speed": 6, "engine": -5},
        {"name": "Balanced Pace", "description": "+2 Speed, Engine -1", "speed": 2, "engine": -1},
        {"name": "Late Stint Gamble", "description": "+4 Speed, Engine -2, Tires -1", "speed": 4, "engine": -2, "tires": -1},
        {"name": "Smooth Sector", "description": "+1 Speed, no wear", "speed": 1},
        {"name": "Tire Conservation", "description": "+2 Speed, Tires +1", "speed": 2, "tires": 1},
        {"name": "Fuel Save Mode", "description": "+1 Speed, Fuel +1", "speed": 1, "fuel": 1},
        {"name": "Calculated Push", "description": "+3 Speed, Engine -1", "speed": 3, "engine": -1},
        {"name": "Patience Setup", "description": "+1 Speed, draw 1 card", "speed": 1, "draw": 1},
        {"name": "Controlled Push", "description": "+2 Speed, Engine -1", "speed": 2, "engine": -1},
        {"name": "Moderate Stint", "description": "+2 Speed, Fuel -1", "speed": 2, "fuel": -1},
        {"name": "Reckless Boost", "description": "+5 Speed, Engine -4, Tires -2", "speed": 5, "engine": -4, "tires": -2},
        {"name": "Engine Overload", "description": "+4 Speed, Engine -3", "speed": 4, "engine": -3}
    ]

    cards = []
    for s in strategies:
        stats = {}
        if "speed" in s:
            stats["speed_modifier"] = s["speed"]
        if "engine" in s:
            stats["engine"] = s["engine"]
        if "tires" in s:
            stats["tires"] = s["tires"]
        if "fuel" in s:
            stats["fuel"] = s["fuel"]
        if "draw" in s:
            stats["draw_cards"] = s["draw"]

        cards.append({
            "name": s["name"],
            "card_type": "strategy",
            "description": s["description"],
            "stats": stats
        })
    return cards

def seed_tactics_cards():
    """Seed tactics cards"""
    tactics = [
        {"name": "Late Brake Dive", "description": "Gain +2 Speed this turn", "speed": 2, "temporary": True},
        {"name": "Underpressure", "description": "Opponent loses -1 Engine", "target": "opponent", "engine": -1},
        {"name": "Clutch Moment", "description": "Gain +1 Reliability", "reliability": 1},
        {"name": "Dirty Air", "description": "Opponent loses -2 Speed this turn", "target": "opponent", "speed": -2, "temporary": True},
        {"name": "Engine Surge", "description": "Gain +3 Speed, Engine -2", "speed": 3, "engine": -2},
        {"name": "No Lift", "description": "Gain +2 Speed, Tires -1", "speed": 2, "tires": -1},
        {"name": "Engine Protect", "description": "Gain +1 Engine", "engine": 1},
        {"name": "Defensive Line", "description": "Block next opponent tactic", "effect": "block"},
        {"name": "Controlled Response", "description": "Gain +1 to all stats", "engine": 1, "tires": 1, "fuel": 1, "reliability": 1},
        {"name": "Long Stint Focus", "description": "Gain +1 Fuel, +1 Tires", "fuel": 1, "tires": 1},
        {"name": "Strategic Lift", "description": "Reduce Engine wear by 1", "engine": 1},
        {"name": "Slipstream Push", "description": "Gain +2 Speed if trailing", "speed": 2, "conditional": "trailing"},
        {"name": "Overcut Attempt", "description": "Gain +1 Speed, draw 1 card", "speed": 1, "draw": 1},
        {"name": "Perfect Line", "description": "Gain +3 Speed, no wear this turn", "speed": 3, "no_wear": True}
    ]

    cards = []
    for t in tactics:
        stats = {}
        if "speed" in t:
            stats["speed_modifier"] = t["speed"]
        if "engine" in t:
            stats["engine"] = t["engine"]
        if "tires" in t:
            stats["tires"] = t["tires"]
        if "fuel" in t:
            stats["fuel"] = t["fuel"]
        if "reliability" in t:
            stats["reliability"] = t["reliability"]
        if "draw" in t:
            stats["draw_cards"] = t["draw"]
        if "effect" in t:
            stats["effect_type"] = t["effect"]
        if "temporary" in t:
            stats["temporary"] = t["temporary"]
        if "conditional" in t:
            stats["conditional"] = t["conditional"]
        if "target" in t:
            stats["target"] = t["target"]

        cards.append({
            "name": t["name"],
            "card_type": "tactics",
            "description": t["description"],
            "stats": stats
        })
    return cards

def seed_event_cards():
    """Seed event cards"""
    events = [
        {"name": "Sudden Rain", "description": "All players: Tires -2"},
        {"name": "Safety Car", "description": "No speed gain this turn, restore 1 stat"},
        {"name": "Track Debris", "description": "Random player: Tires -1"},
        {"name": "Mechanical Glitch", "description": "Reliability check required"},
        {"name": "Slipstream Chance", "description": "Trailing player: +3 Speed"},
        {"name": "Pit Lane Delay", "description": "Next pit stop costs 1 extra turn"}
    ]

    cards = []
    for e in events:
        cards.append({
            "name": e["name"],
            "card_type": "event",
            "description": e["description"],
            "stats": {}
        })
    return cards

def main():
    with app.app_context():
        print("Starting card seed process...")

        # Check for --force flag
        force = '--force' in sys.argv

        # Check if cards already exist
        existing_count = Card.query.count()
        if existing_count > 0:
            print(f"WARNING: Found {existing_count} existing cards.")
            if not force:
                response = input("Delete existing cards and reseed? (yes/no): ")
                if response.lower() != 'yes':
                    print("Seed cancelled.")
                    return

            # Delete existing cards
            Card.query.delete()
            db.session.commit()
            print("Deleted existing cards.")

        # Combine all cards
        all_cards = []
        all_cards.extend(seed_cars())
        all_cards.extend(seed_strategy_cards())
        all_cards.extend(seed_tactics_cards())
        all_cards.extend(seed_event_cards())

        # Add cards to database
        print(f"Adding {len(all_cards)} cards...")

        for card_data in all_cards:
            card = Card(
                name=card_data["name"],
                card_type=card_data["card_type"],
                description=card_data["description"],
                stats=card_data.get("stats", {})
            )
            db.session.add(card)

        db.session.commit()

        # Print summary
        print("\nSeed complete!")
        print(f"   Cars: {Card.query.filter_by(card_type='car').count()}")
        print(f"   Strategy: {Card.query.filter_by(card_type='strategy').count()}")
        print(f"   Tactics: {Card.query.filter_by(card_type='tactics').count()}")
        print(f"   Events: {Card.query.filter_by(card_type='event').count()}")
        print(f"   Total: {Card.query.count()}")
        print("\nYou can now build your decks!")

if __name__ == "__main__":
    main()
