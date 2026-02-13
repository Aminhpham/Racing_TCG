"""
Setup script to:
1. Clean up orphaned card IDs from existing decks
2. Create 4 starter decks

Run with: python setup_starter_decks.py
"""

import sys
from app import create_app, db
from app.models import Deck, Card, User

app = create_app()


def cleanup_orphaned_cards():
    """Remove card IDs that reference deleted cards"""
    with app.app_context():
        print("Cleaning up orphaned card IDs...")

        # Get all valid card IDs
        valid_card_ids = {card.id for card in Card.query.all()}

        # Check all decks
        decks = Deck.query.all()
        fixed_count = 0

        for deck in decks:
            if deck.card_ids:
                original_count = len(deck.card_ids)
                # Keep only valid card IDs
                deck.card_ids = [cid for cid in deck.card_ids if cid in valid_card_ids]

                if len(deck.card_ids) != original_count:
                    from sqlalchemy.orm.attributes import flag_modified
                    flag_modified(deck, 'card_ids')
                    removed = original_count - len(deck.card_ids)
                    print(f"  Fixed deck '{deck.name}': removed {removed} orphaned cards")
                    fixed_count += 1

        if fixed_count > 0:
            db.session.commit()
            print(f"Fixed {fixed_count} deck(s)")
        else:
            print("No orphaned cards found!")


def create_starter_decks():
    """Create 4 pre-built starter decks"""
    with app.app_context():
        print("\nCreating starter decks...")

        # Get the first user (or create a system user)
        user = User.query.first()
        if not user:
            print("ERROR: No users found. Please create a user account first.")
            return

        # Get cards by type
        cars = Card.query.filter_by(card_type='car').all()
        strategies = Card.query.filter_by(card_type='strategy').all()
        tactics = Card.query.filter_by(card_type='tactics').all()
        events = Card.query.filter_by(card_type='event').all()

        if len(cars) < 1 or len(strategies) < 10 or len(tactics) < 10:
            print("ERROR: Not enough cards in database. Run seed_all_cards.py first.")
            return

        # Delete existing starter decks
        Deck.query.filter(Deck.name.like('Starter:%')).delete()
        db.session.commit()

        # Starter Deck 1: Aggressive Racer
        deck1 = Deck(
            user_id=user.id,
            name="Starter: Aggressive Racer",
            description="High-speed aggressive deck focused on maximum speed",
            card_ids=[cars[1].id] + [s.id for s in strategies[:7]] + [t.id for t in tactics[:7]] + [e.id for e in events[:3]]
        )

        # Ensure exactly 40 cards
        while len(deck1.card_ids) < 40:
            deck1.card_ids.append(strategies[len(deck1.card_ids) % len(strategies)].id)
        deck1.card_ids = deck1.card_ids[:40]

        # Starter Deck 2: Balanced Racer
        deck2 = Deck(
            user_id=user.id,
            name="Starter: Balanced Racer",
            description="Well-rounded deck with balanced strategy",
            card_ids=[cars[0].id] + [s.id for s in strategies[5:12]] + [t.id for t in tactics[5:12]] + [e.id for e in events[:3]]
        )

        while len(deck2.card_ids) < 40:
            deck2.card_ids.append(strategies[len(deck2.card_ids) % len(strategies)].id)
        deck2.card_ids = deck2.card_ids[:40]

        # Starter Deck 3: Defensive Racer
        deck3 = Deck(
            user_id=user.id,
            name="Starter: Defensive Racer",
            description="Conservative deck focused on reliability and endurance",
            card_ids=[cars[3].id] + [s.id for s in strategies[8:]] + [t.id for t in tactics[8:]] + [e.id for e in events[:4]]
        )

        while len(deck3.card_ids) < 40:
            deck3.card_ids.append(tactics[len(deck3.card_ids) % len(tactics)].id)
        deck3.card_ids = deck3.card_ids[:40]

        # Starter Deck 4: Mixed Strategy
        deck4 = Deck(
            user_id=user.id,
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

        print("Created 4 starter decks:")
        print("  1. Starter: Aggressive Racer (40 cards)")
        print("  2. Starter: Balanced Racer (40 cards)")
        print("  3. Starter: Defensive Racer (40 cards)")
        print("  4. Starter: Mixed Strategy (40 cards)")
        print("\nStarter decks are ready to use!")


def main():
    # Clean up orphaned cards first
    cleanup_orphaned_cards()

    # Create starter decks
    create_starter_decks()


if __name__ == "__main__":
    main()
