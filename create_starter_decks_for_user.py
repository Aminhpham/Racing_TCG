"""
Create starter decks for a specific user or all users.
Run with: python create_starter_decks_for_user.py
"""

import sys
from app import create_app, db
from app.models import Deck, Card, User

app = create_app()


def create_starter_decks_for_user(user_id):
    """Create 4 starter decks for a specific user"""
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            print(f"ERROR: User with ID {user_id} not found.")
            return False

        # Get cards by type
        cars = Card.query.filter_by(card_type='car').all()
        strategies = Card.query.filter_by(card_type='strategy').all()
        tactics = Card.query.filter_by(card_type='tactics').all()
        events = Card.query.filter_by(card_type='event').all()

        if len(cars) < 1 or len(strategies) < 10 or len(tactics) < 10:
            print("ERROR: Not enough cards in database. Run seed_all_cards.py first.")
            return False

        # Delete existing starter decks for this user
        Deck.query.filter(Deck.user_id == user_id, Deck.name.like('Starter:%')).delete()
        db.session.commit()

        # Starter Deck 1: Aggressive Racer
        deck1 = Deck(
            user_id=user_id,
            name="Starter: Aggressive Racer",
            description="High-speed aggressive deck focused on maximum speed",
            card_ids=[cars[1].id] + [s.id for s in strategies[:7]] + [t.id for t in tactics[:7]] + [e.id for e in events[:3]]
        )
        while len(deck1.card_ids) < 40:
            deck1.card_ids.append(strategies[len(deck1.card_ids) % len(strategies)].id)
        deck1.card_ids = deck1.card_ids[:40]

        # Starter Deck 2: Balanced Racer
        deck2 = Deck(
            user_id=user_id,
            name="Starter: Balanced Racer",
            description="Well-rounded deck with balanced strategy",
            card_ids=[cars[0].id] + [s.id for s in strategies[5:12]] + [t.id for t in tactics[5:12]] + [e.id for e in events[:3]]
        )
        while len(deck2.card_ids) < 40:
            deck2.card_ids.append(strategies[len(deck2.card_ids) % len(strategies)].id)
        deck2.card_ids = deck2.card_ids[:40]

        # Starter Deck 3: Defensive Racer
        deck3 = Deck(
            user_id=user_id,
            name="Starter: Defensive Racer",
            description="Conservative deck focused on reliability and endurance",
            card_ids=[cars[3].id] + [s.id for s in strategies[8:]] + [t.id for t in tactics[8:]] + [e.id for e in events[:4]]
        )
        while len(deck3.card_ids) < 40:
            deck3.card_ids.append(tactics[len(deck3.card_ids) % len(tactics)].id)
        deck3.card_ids = deck3.card_ids[:40]

        # Starter Deck 4: Mixed Strategy
        deck4 = Deck(
            user_id=user_id,
            name="Starter: Mixed Strategy",
            description="Versatile deck with mix of all card types",
            card_ids=[cars[2].id] + [s.id for s in strategies[::2][:8]] + [t.id for t in tactics[::2][:8]] + [e.id for e in events[:4]]
        )
        while len(deck4.card_ids) < 40:
            deck4.card_ids.append(strategies[len(deck4.card_ids) % len(strategies)].id)
        deck4.card_ids = deck4.card_ids[:40]

        # Add all decks
        db.session.add(deck1)
        db.session.add(deck2)
        db.session.add(deck3)
        db.session.add(deck4)
        db.session.commit()

        print(f"Created 4 starter decks for user '{user.username}' (ID: {user_id})")
        return True


def create_starter_decks_for_all_users():
    """Create starter decks for all users who don't have them"""
    with app.app_context():
        users = User.query.all()
        if not users:
            print("No users found in database.")
            return

        print(f"Found {len(users)} user(s)")

        for user in users:
            # Check if user already has starter decks
            existing_starters = Deck.query.filter(
                Deck.user_id == user.id,
                Deck.name.like('Starter:%')
            ).count()

            if existing_starters > 0:
                print(f"User '{user.username}' already has {existing_starters} starter deck(s), skipping...")
                continue

            create_starter_decks_for_user(user.id)

        print("\nDone! All users now have starter decks.")


def main():
    with app.app_context():
        print("Starter Deck Creator\n")

        # Check if user specified a user ID
        if len(sys.argv) > 1:
            try:
                user_id = int(sys.argv[1])
                create_starter_decks_for_user(user_id)
            except ValueError:
                print("Invalid user ID. Usage: python create_starter_decks_for_user.py [user_id]")
        else:
            # Create for all users
            create_starter_decks_for_all_users()


if __name__ == "__main__":
    main()
