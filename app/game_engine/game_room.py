from typing import Dict, List, Optional
import random
from datetime import datetime
from .player_state import PlayerState


class GameRoom:
    """Represents a single active game between two players"""

    def __init__(self, match_id: int, player1_id: int, player2_id: int,
                 player1_car: dict, player2_car: dict,
                 player1_deck: List[int], player2_deck: List[int]):
        self.match_id = match_id
        self.player1_id = player1_id
        self.player2_id = player2_id

        # Game phase tracking
        self.current_phase = "strategy_selection"
        self.current_turn = 1
        self.active_player_id = None  # Used in react phase

        # Player states
        self.player_states = {
            player1_id: PlayerState(player1_id, player1_car, player1_deck),
            player2_id: PlayerState(player2_id, player2_car, player2_deck)
        }

        # Temporary phase data
        self.strategy_selections = {}  # {player_id: card_id}
        self.ready_flags = {player1_id: False, player2_id: False}
        self.pass_flags = {player1_id: False, player2_id: False}

        # Determine initial leader (random)
        self.leader_id = random.choice([player1_id, player2_id])
        self.player_states[self.leader_id].is_leader = True

        # Connection tracking
        self.connected_players = {player1_id: True, player2_id: True}

        # Turn history for logging
        self.turn_history = []

        # Game over flag
        self.game_over = False
        self.winner_id = None
        self.win_condition = None

    def get_opponent_id(self, player_id: int) -> int:
        """Get the opponent's ID"""
        return self.player2_id if player_id == self.player1_id else self.player1_id

    def select_strategy_card(self, player_id: int, card_id: int) -> bool:
        """Player selects their strategy card (hidden until reveal)"""
        player_state = self.player_states[player_id]

        if self.current_phase != "strategy_selection":
            return False

        if card_id not in player_state.hand:
            return False

        self.strategy_selections[player_id] = card_id
        return True

    def ready_for_reveal(self, player_id: int) -> Optional[dict]:
        """Mark player as ready, reveal if both ready"""
        if self.current_phase != "strategy_selection":
            return None

        if player_id not in self.strategy_selections:
            return None

        self.ready_flags[player_id] = True

        if all(self.ready_flags.values()):
            return self.reveal_strategy_cards()
        return None

    def reveal_strategy_cards(self) -> dict:
        """Reveal both players' strategy cards and apply effects"""
        from .card_effects import apply_strategy_card, get_card_data

        results = {}
        for player_id, card_id in self.strategy_selections.items():
            player_state = self.player_states[player_id]
            card_data = get_card_data(card_id)

            # Apply card effects
            changes = apply_strategy_card(player_state, card_data)

            # Move card from hand to discard
            player_state.hand.remove(card_id)
            player_state.discard.append(card_id)

            results[player_id] = {
                "card": card_data,
                "changes": changes,
                "new_stats": player_state.car_stats.copy()
            }

        # Log event
        self.turn_history.append({
            "turn": self.current_turn,
            "phase": "strategy_reveal",
            "selections": self.strategy_selections.copy(),
            "results": results
        })

        # Transition to react phase
        self.current_phase = "react"
        self.active_player_id = self.leader_id
        self.strategy_selections.clear()
        self.ready_flags = {self.player1_id: False, self.player2_id: False}
        self.pass_flags = {self.player1_id: False, self.player2_id: False}

        return results

    def play_tactic_card(self, player_id: int, card_id: int, target: str = "self") -> dict:
        """Play a tactic card during react phase"""
        from .card_effects import apply_tactic_card, get_card_data

        if self.current_phase != "react":
            raise ValueError("Not in react phase")

        if player_id != self.active_player_id:
            raise ValueError("Not your turn in react phase")

        player_state = self.player_states[player_id]
        opponent_state = self.player_states[self.get_opponent_id(player_id)]

        if card_id not in player_state.hand:
            raise ValueError("Card not in hand")

        card_data = get_card_data(card_id)

        # Apply card effect
        effect_result = apply_tactic_card(player_state, opponent_state, card_data, target)

        # Remove from hand, add to discard
        player_state.hand.remove(card_id)
        player_state.discard.append(card_id)
        player_state.played_tactics_this_turn.append(card_id)

        # Log event
        self.turn_history.append({
            "turn": self.current_turn,
            "phase": "react",
            "player_id": player_id,
            "card_id": card_id,
            "effect": effect_result
        })

        # Reset pass flag for this player since they took an action
        self.pass_flags[player_id] = False

        # Switch active player
        self.active_player_id = self.get_opponent_id(player_id)

        return effect_result

    def pass_react_phase(self, player_id: int) -> Optional[dict]:
        """Player passes their react phase turn"""
        if self.current_phase != "react":
            return None

        if player_id != self.active_player_id:
            return None

        # Mark this player as passed
        self.pass_flags[player_id] = True

        # Check if both players have passed
        if all(self.pass_flags.values()):
            # Both passed, move to speed phase
            return self.transition_to_speed_phase()
        else:
            # Switch to opponent
            self.active_player_id = self.get_opponent_id(player_id)
            return None

    def transition_to_speed_phase(self) -> dict:
        """Calculate movement and wear for both players"""
        from .speed_calculator import calculate_speed_phase

        self.current_phase = "speed_calculation"
        results = calculate_speed_phase(self)

        # Log event
        self.turn_history.append({
            "turn": self.current_turn,
            "phase": "speed_calculation",
            "results": results
        })

        # Check for lap completion (handle multiple laps if needed)
        for player_id in [self.player1_id, self.player2_id]:
            player_state = self.player_states[player_id]
            laps_completed = []
            while player_state.lap_progress >= 10:
                lap_result = self.handle_lap_completion(player_id)
                laps_completed.append(lap_result)
            if laps_completed:
                results[f"{player_id}_lap_completion"] = laps_completed

        # Check for game over
        game_over_result = self.check_game_over()
        if game_over_result:
            return {**results, "game_over": game_over_result}

        # Start new turn if game continues
        self.start_new_turn()

        return results

    def handle_lap_completion(self, player_id: int) -> dict:
        """Handle lap completion logic"""
        player_state = self.player_states[player_id]

        # Calculate overflow (how much progress beyond 10)
        overflow = player_state.lap_progress - 10

        # Increment lap
        player_state.current_lap += 1

        # Set progress to overflow
        player_state.lap_progress = overflow

        # Apply wear: lose 1 Fuel and 1 Tire per lap
        player_state.apply_stat_change("fuel", -1)
        player_state.apply_stat_change("tires", -1)

        # Check for reliability if any stat is at 0
        reliability_result = self.check_reliability(player_id)

        # Log lap completion
        self.turn_history.append({
            "turn": self.current_turn,
            "event": "lap_completed",
            "player_id": player_id,
            "lap": player_state.current_lap,
            "overflow": overflow,
            "reliability": reliability_result
        })

        return {
            "lap": player_state.current_lap,
            "overflow": overflow,
            "new_progress": player_state.lap_progress,
            "reliability": reliability_result
        }

    def check_reliability(self, player_id: int) -> Optional[dict]:
        """Check if player needs to make reliability check"""
        player_state = self.player_states[player_id]

        # Check if any stat is at 0
        stats_at_zero = [stat for stat, value in player_state.car_stats.items() if value == 0]

        if not stats_at_zero:
            return None

        # Roll d6
        roll = random.randint(1, 6)
        reliability_threshold = player_state.car_stats["reliability"]

        # Success if roll >= reliability threshold
        success = roll >= reliability_threshold

        if success:
            # Enter limp mode
            player_state.in_limp_mode = True
            player_state.limp_mode_turns = 0
        else:
            # Failure: player loses
            self.end_game(self.get_opponent_id(player_id), "reliability_failure")

        return {
            "roll": roll,
            "threshold": reliability_threshold,
            "success": success,
            "stats_at_zero": stats_at_zero
        }

    def check_game_over(self) -> Optional[dict]:
        """Check if game is over and determine winner"""
        # Check if either player completed all 8 laps (current_lap becomes 9)
        for player_id, player_state in self.player_states.items():
            if player_state.current_lap > 8:
                self.end_game(player_id, "lap_completion")
                return {
                    "winner_id": player_id,
                    "condition": "lap_completion"
                }

        return None

    def end_game(self, winner_id: int, condition: str):
        """End the game and mark winner"""
        self.game_over = True
        self.winner_id = winner_id
        self.win_condition = condition
        self.current_phase = "game_over"

        # Save final state to DB
        self.save_to_db(winner_id, condition)

    def start_new_turn(self):
        """Start a new turn"""
        self.current_turn += 1
        self.current_phase = "strategy_selection"

        # Reset flags
        self.strategy_selections.clear()
        self.ready_flags = {self.player1_id: False, self.player2_id: False}
        self.pass_flags = {self.player1_id: False, self.player2_id: False}

        # Draw cards for each player (skip first turn for first player)
        for player_id, player_state in self.player_states.items():
            if self.current_turn > 1 or player_id != self.player1_id:
                player_state.draw_cards(2)

            # Reset played tactics
            player_state.played_tactics_this_turn = []

            # Update limp mode
            if player_state.in_limp_mode:
                player_state.limp_mode_turns += 1
                if player_state.limp_mode_turns > 2:
                    # Force reliability check
                    self.check_reliability(player_id)

    def save_to_db(self, winner_id: int = None, win_condition: str = None):
        """Persist game state to database"""
        from app import db
        from app.models import GameMatch, GameState

        match = GameMatch.query.get(self.match_id)
        if not match:
            return

        if winner_id:
            match.status = "completed"
            match.winner_id = winner_id
            match.win_condition = win_condition
            match.completed_at = datetime.utcnow()
        else:
            match.status = "active"
            if not match.started_at:
                match.started_at = datetime.utcnow()

        # Save game state
        state_data = {
            "player1": self.player_states[self.player1_id].to_dict(),
            "player2": self.player_states[self.player2_id].to_dict(),
            "turn_history": self.turn_history,
            "current_phase": self.current_phase,
            "current_turn": self.current_turn,
            "leader_id": self.leader_id
        }

        game_state = GameState.query.filter_by(match_id=self.match_id).first()
        if not game_state:
            game_state = GameState(match_id=self.match_id)

        game_state.current_phase = self.current_phase
        game_state.current_turn = self.current_turn
        game_state.active_player_id = self.active_player_id
        game_state.state_data = state_data

        db.session.add(game_state)
        db.session.commit()

    def get_sanitized_state(self, for_player_id: int) -> dict:
        """Get game state with hidden opponent information"""
        player_state = self.player_states[for_player_id]
        opponent_id = self.get_opponent_id(for_player_id)
        opponent_state = self.player_states[opponent_id]

        return {
            "match_id": self.match_id,
            "phase": self.current_phase,
            "turn": self.current_turn,
            "can_act": self.active_player_id == for_player_id if self.current_phase == "react" else True,
            "is_leader": player_state.is_leader,
            "your_state": player_state.to_dict(hide_secrets=False),
            "opponent_state": opponent_state.to_dict(hide_secrets=True),
            "game_over": self.game_over,
            "winner_id": self.winner_id if self.game_over else None,
            "win_condition": self.win_condition if self.game_over else None
        }
