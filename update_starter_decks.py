"""
Update existing starter decks with new card IDs after reseeding.
This updates in-place to avoid foreign key constraint issues.
Run with: python update_starter_decks.py
"""

from app import create_app, db
from app.models import Deck, Card, User
from sqlalchemy.orm.attributes import flag_modified

app = create_app()


def update_starter_deck(deck, new_card_ids):
    """Update a deck's card_ids in-place"""
    deck.card_ids = new_card_ids
    flag_modified(deck, 'card_ids')


def update_all_starter_decks():
    """Update all starter decks with new card IDs"""
    with app.app_context():
        # Get cards by type
        cars = Card.query.filter_by(card_type='car').all()
        strategies = Card.query.filter_by(card_type='strategy').all()
        tactics = Card.query.filter_by(card_type='tactics').all()
        events = Card.query.filter_by(card_type='event').all()

        if len(cars) < 4 or len(strategies) < 10 or len(tactics) < 10:
            print("ERROR: Not enough cards in database.")
            return False

        # Find all starter decks
        all_users = User.query.all()

        for user in all_users:
            print(f"\nUpdating starter decks for user: {user.username}")

            # Find this user's starter decks by name
            aggressive = Deck.query.filter_by(user_id=user.id, name="Starter: Aggressive Racer").first()
            balanced = Deck.query.filter_by(user_id=user.id, name="Starter: Balanced Racer").first()
            defensive = Deck.query.filter_by(user_id=user.id, name="Starter: Defensive Racer").first()
            mixed = Deck.query.filter_by(user_id=user.id, name="Starter: Mixed Strategy").first()

            # Update Aggressive Racer
            if aggressive:
                new_ids = [cars[1].id] + [s.id for s in strategies[:7]] + [t.id for t in tactics[:7]] + [e.id for e in events[:3]]
                while len(new_ids) < 40:
                    new_ids.append(strategies[len(new_ids) % len(strategies)].id)
                new_ids = new_ids[:40]
                update_starter_deck(aggressive, new_ids)
                print(f"  Updated: Aggressive Racer ({len(new_ids)} cards)")

            # Update Balanced Racer
            if balanced:
                new_ids = [cars[0].id] + [s.id for s in strategies[5:12]] + [t.id for t in tactics[5:12]] + [e.id for e in events[:3]]
                while len(new_ids) < 40:
                    new_ids.append(strategies[len(new_ids) % len(strategies)].id)
                new_ids = new_ids[:40]
                update_starter_deck(balanced, new_ids)
                print(f"  Updated: Balanced Racer ({len(new_ids)} cards)")

            # Update Defensive Racer
            if defensive:
                new_ids = [cars[3].id] + [s.id for s in strategies[8:]] + [t.id for t in tactics[8:]] + [e.id for e in events[:4]]
                while len(new_ids) < 40:
                    new_ids.append(tactics[len(new_ids) % len(tactics)].id)
                new_ids = new_ids[:40]
                update_starter_deck(defensive, new_ids)
                print(f"  Updated: Defensive Racer ({len(new_ids)} cards)")

            # Update Mixed Strategy
            if mixed:
                new_ids = [cars[2].id] + [s.id for s in strategies[::2][:8]] + [t.id for t in tactics[::2][:8]] + [e.id for e in events[:4]]
                while len(new_ids) < 40:
                    new_ids.append(strategies[len(new_ids) % len(strategies)].id)
                new_ids = new_ids[:40]
                update_starter_deck(mixed, new_ids)
                print(f"  Updated: Mixed Strategy ({len(new_ids)} cards)")

        # Commit all changes
        db.session.commit()
        print("\nAll starter decks updated successfully!")
        return True


if __name__ == "__main__":
    print("Starter Deck Update Script\n")
    print("This will update all existing starter decks with new card IDs.\n")
    update_all_starter_decks()
