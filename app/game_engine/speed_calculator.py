import random
from typing import Dict


def calculate_speed_phase(game_room) -> Dict:
    """Calculate movement and wear for both players"""
    results = {}

    for player_id, player_state in game_room.player_states.items():
        # Calculate base speed from car stats
        engine = player_state.car_stats["engine"]
        tires = player_state.car_stats["tires"]
        fuel = player_state.car_stats["fuel"]

        # Base speed is capped at 5 (before modifiers)
        base_speed = min(5, engine + tires + fuel)

        # Apply limp mode penalty
        if player_state.in_limp_mode:
            base_speed -= 1

        # Slipstream bonus (trailing player)
        slipstream = calculate_slipstream(game_room, player_id)

        # Apply speed modifier from strategy card
        speed_modifier = player_state.speed_modifier

        # Total movement
        total_movement = max(0, base_speed + slipstream + speed_modifier)

        # Store current speed for UI display
        player_state.current_speed = total_movement

        # Update lap progress
        old_progress = player_state.lap_progress
        player_state.lap_progress += total_movement

        # Calculate wear (engine wear already applied from cards)
        # No additional wear in this simplified version

        # Reliability check if any stat is at 0
        reliability_result = None
        if any(value <= 0 for value in [engine, tires, fuel]):
            reliability_result = perform_reliability_check(player_state)

        results[player_id] = {
            "base_speed": base_speed,
            "slipstream": slipstream,
            "total_movement": total_movement,
            "old_progress": old_progress,
            "new_progress": player_state.lap_progress,
            "current_lap": player_state.current_lap,
            "reliability_check": reliability_result
        }

    # Update leader status
    update_leader_status(game_room)

    return results


def calculate_slipstream(game_room, player_id: int) -> int:
    """Calculate slipstream bonus for a player"""
    player_state = game_room.player_states[player_id]
    opponent_id = game_room.get_opponent_id(player_id)
    opponent_state = game_room.player_states[opponent_id]

    # Calculate total progress for both players
    player_total = (player_state.current_lap * 10 +
                    player_state.lap_progress)
    opponent_total = (opponent_state.current_lap * 10 +
                      opponent_state.lap_progress)

    # If trailing
    if player_total < opponent_total:
        gap = opponent_total - player_total
        if gap >= 5:
            return 2  # Large gap: +2 speed
        else:
            return 1  # Small gap: +1 speed

    return 0  # Leading or tied: no slipstream


def update_leader_status(game_room):
    """Update who is the leader based on lap progress"""
    p1_state = game_room.player_states[game_room.player1_id]
    p2_state = game_room.player_states[game_room.player2_id]

    p1_total = p1_state.current_lap * 10 + p1_state.lap_progress
    p2_total = p2_state.current_lap * 10 + p2_state.lap_progress

    if p1_total > p2_total:
        p1_state.is_leader = True
        p2_state.is_leader = False
        game_room.leader_id = game_room.player1_id
    elif p2_total > p1_total:
        p1_state.is_leader = False
        p2_state.is_leader = True
        game_room.leader_id = game_room.player2_id
    # If tied, leader status doesn't change


def perform_reliability_check(player_state) -> Dict:
    """Perform reliability check when stats are at 0"""
    # Find which stats are at 0
    stats_at_zero = [
        stat for stat, value in player_state.car_stats.items()
        if value <= 0
    ]

    if not stats_at_zero or player_state.car_stats["reliability"] <= 0:
        # Auto-fail if reliability is 0
        return {
            "required": True,
            "roll": 0,
            "threshold": player_state.car_stats["reliability"],
            "success": False,
            "stats_at_zero": stats_at_zero
        }

    # Roll d6
    roll = random.randint(1, 6)
    reliability_threshold = player_state.car_stats["reliability"]

    # Success if roll >= reliability threshold
    success = roll >= reliability_threshold

    result = {
        "required": True,
        "roll": roll,
        "threshold": reliability_threshold,
        "success": success,
        "stats_at_zero": stats_at_zero
    }

    if success:
        # Enter limp mode
        player_state.in_limp_mode = True
        player_state.limp_mode_turns = 0
    # If failure, game will end (handled in GameRoom)

    return result
