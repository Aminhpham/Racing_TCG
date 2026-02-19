import random


class PlayerState:
    """Represents one player's state in a game"""

    def __init__(self, player_id: int, car_data: dict, deck_card_ids: list):
        self.player_id = player_id

        # Car stats (initialized from car_data)
        self.car_stats = {
            "base_speed": car_data.get("base_speed", 3),
            "engine": car_data.get("engine", 8),
            "tires": car_data.get("tires", 6),
            "fuel": car_data.get("fuel", 6),
            "reliability": car_data.get("reliability", 3)
        }

        # Store car ability for later use
        self.car_ability = car_data.get("ability", "")

        # Position tracking
        self.current_lap = 1
        self.lap_progress = 0  # 0-10 per lap
        self.is_leader = False
        # Initialize current_speed from base_speed (modified by cards each turn)
        self.current_speed = car_data.get("base_speed", 3)

        # Deck management
        self.deck = deck_card_ids.copy()
        random.shuffle(self.deck)
        self.hand = []
        self.discard = []

        # Draw starting hand (5 cards)
        self.draw_cards(5)

        # Resources (for pit stops and special abilities)
        self.resources = 5

        # Wear tracking
        self.wear_accumulated = 0

        # Limp mode tracking
        self.in_limp_mode = False
        self.limp_mode_turns = 0

        # Temporary phase data
        self.selected_strategy_card = None
        self.played_tactics_this_turn = []

        # Speed modifier from strategy card (resets each turn)
        self.speed_modifier = 0

    def draw_cards(self, count: int):
        """Draw cards from deck to hand"""
        for _ in range(count):
            if len(self.hand) >= 7:  # Hand limit
                break

            if not self.deck:
                # Reshuffle discard into deck
                if self.discard:
                    self.deck = self.discard.copy()
                    random.shuffle(self.deck)
                    self.discard = []
                else:
                    break  # No cards left

            if self.deck:
                self.hand.append(self.deck.pop())

    def apply_stat_change(self, stat_name: str, change: int):
        """Apply a change to a car stat, respecting bounds"""
        if stat_name in self.car_stats:
            old_value = self.car_stats[stat_name]
            new_value = max(0, min(10, old_value + change))
            self.car_stats[stat_name] = new_value
            return new_value - old_value
        return 0

    def apply_wear(self, wear_amount: int):
        """Apply wear damage to car stats"""
        self.wear_accumulated += wear_amount

    def pit_stop(self, pit_type: str = "normal"):
        """Perform a pit stop"""
        if pit_type == "normal" and self.resources >= 2:
            # Normal pit: costs 2 resources, choose 2 repairs
            self.resources -= 2
            return True
        elif pit_type == "fast" and self.resources >= 1:
            # Fast pit: costs 1 resource, 50% chance of failure
            self.resources -= 1
            return True
        elif pit_type == "full" and self.resources >= 3:
            # Full service: costs 3 resources, reset all wear
            self.resources -= 3
            self.car_stats["engine"] = 8
            self.car_stats["tires"] = 6
            self.car_stats["fuel"] = 6
            self.in_limp_mode = False
            self.limp_mode_turns = 0
            return True
        return False

    def to_dict(self, hide_secrets: bool = False):
        """Convert to dictionary (optionally hide hand/deck)"""
        data = {
            "player_id": self.player_id,
            "car_stats": self.car_stats.copy(),
            "car_ability": self.car_ability,
            "current_lap": self.current_lap,
            "lap_progress": self.lap_progress,
            "current_speed": self.current_speed,
            "is_leader": self.is_leader,
            "hand_size": len(self.hand),
            "deck_size": len(self.deck),
            "discard_size": len(self.discard),
            "resources": self.resources,
            "wear_accumulated": self.wear_accumulated,
            "in_limp_mode": self.in_limp_mode,
            "limp_mode_turns": self.limp_mode_turns
        }

        if not hide_secrets:
            # Include full card data for hand (not just IDs)
            data["hand"] = self._get_card_data_list(self.hand)
            data["deck"] = self.deck
            data["discard"] = self.discard
            data["selected_strategy"] = self.selected_strategy_card

        return data

    def _get_card_data_list(self, card_ids: list) -> list:
        """Get full card data for a list of card IDs"""
        from app.models import Card

        if not card_ids:
            return []

        cards = Card.query.filter(Card.id.in_(card_ids)).all()
        card_dict = {card.id: card for card in cards}

        # Return cards in the same order as card_ids
        return [
            {
                "id": card_id,
                "name": (card_dict[card_id].name if card_id in card_dict
                         else "Unknown Card"),
                "card_type": (card_dict[card_id].card_type
                              if card_id in card_dict else "unknown"),
                "description": (card_dict[card_id].description
                                if card_id in card_dict else ""),
                "stats": (card_dict[card_id].stats
                          if card_id in card_dict else {})
            }
            for card_id in card_ids
        ]

    def from_dict(self, data: dict):
        """Restore state from dictionary"""
        self.player_id = data["player_id"]
        self.car_stats = data["car_stats"]
        self.car_ability = data.get("car_ability", "")
        self.current_lap = data["current_lap"]
        self.lap_progress = data["lap_progress"]
        self.is_leader = data["is_leader"]
        self.resources = data["resources"]
        self.wear_accumulated = data["wear_accumulated"]
        self.in_limp_mode = data.get("in_limp_mode", False)
        self.limp_mode_turns = data.get("limp_mode_turns", 0)

        if "hand" in data:
            self.hand = data["hand"]
        if "deck" in data:
            self.deck = data["deck"]
        if "discard" in data:
            self.discard = data["discard"]
        if "selected_strategy" in data:
            self.selected_strategy_card = data["selected_strategy"]
