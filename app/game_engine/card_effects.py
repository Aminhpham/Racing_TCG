import random
from typing import Dict, Optional

# Card cache for performance
CARD_CACHE = {}


def get_card_data(card_id: int) -> dict:
    """Fetch card data from database (with caching)"""
    if card_id in CARD_CACHE:
        return CARD_CACHE[card_id]

    from app.models import Card
    card = Card.query.get(card_id)

    if not card:
        return {"id": card_id, "name": "Unknown", "card_type": "unknown", "stats": {}}

    card_data = {
        "id": card.id,
        "name": card.name,
        "card_type": card.card_type,
        "stats": card.stats or {},
        "description": card.description or "",
        "requirements": card.requirements or {}
    }

    CARD_CACHE[card_id] = card_data
    return card_data


def clear_card_cache():
    """Clear the card cache (useful for testing)"""
    global CARD_CACHE
    CARD_CACHE = {}


def apply_strategy_card(player_state, card_data: dict) -> dict:
    """Apply strategy card effects to player's car stats and return detailed changes"""
    stats = card_data.get("stats", {})
    stat_changes = {}
    changes = {}

    # Apply speed modifier (stored for speed calculation)
    if "speed_modifier" in stats:
        changes["speed_modifier"] = stats["speed_modifier"]

    # Apply engine wear
    if "engine_wear" in stats:
        engine_change = -stats["engine_wear"]
        actual_change = player_state.apply_stat_change("engine", engine_change)
        changes["engine"] = actual_change
        stat_changes["engine"] = actual_change

    # Apply other stat changes with detailed tracking
    if "engine" in stats:
        old_value = player_state.car_stats.get("engine", 0)
        actual_change = player_state.apply_stat_change("engine", stats["engine"])
        changes["engine"] = actual_change
        stat_changes["engine"] = actual_change

    for stat_name in ["tires", "fuel", "reliability"]:
        if stat_name in stats:
            old_value = player_state.car_stats.get(stat_name, 0)
            actual_change = player_state.apply_stat_change(stat_name, stats[stat_name])
            changes[stat_name] = actual_change
            stat_changes[stat_name] = actual_change

    # Handle special effects
    effect_type = stats.get("effect_type")

    if effect_type == "conditional_wear":
        # Some cards have conditional wear (e.g., based on dice roll)
        if "roll_condition" in stats:
            roll = random.randint(1, 6)
            changes["dice_roll"] = roll

            roll_range = stats["roll_condition"]  # e.g., "1-2"
            if "-" in roll_range:
                low, high = map(int, roll_range.split("-"))
                if low <= roll <= high:
                    # Apply conditional wear
                    conditional_wear = stats.get("conditional_wear_amount", 1)
                    actual_change = player_state.apply_stat_change("engine", -conditional_wear)
                    changes["conditional_engine"] = actual_change

    elif effect_type == "draw_cards":
        # Draw additional cards
        draw_count = stats.get("draw_count", 1)
        player_state.draw_cards(draw_count)
        changes["cards_drawn"] = draw_count

    # Return detailed result for UI feedback
    return {
        "card_name": card_data.get("name", "Unknown"),
        "description": card_data.get("description", ""),
        "stat_changes": stat_changes,
        "raw_changes": changes  # Keep original changes for backwards compatibility
    }


def apply_tactic_card(player_state, opponent_state, card_data: dict, target: str) -> dict:
    """Apply tactic card effect and return detailed result"""
    stats = card_data.get("stats", {})
    effect_type = stats.get("effect_type", "add_stats")

    result = {
        "card_name": card_data["name"],
        "description": card_data.get("description", ""),
        "effect_type": effect_type,
        "target": target,
        "stat_changes": {},
        "changes": {}  # Keep for backwards compatibility
    }

    target_state = player_state if target == "self" else opponent_state

    # Handle different effect types
    if effect_type == "add_stats":
        # Add or subtract stats
        for stat in ["engine", "tires", "fuel", "reliability"]:
            if stat in stats:
                change = stats[stat]
                actual_change = target_state.apply_stat_change(stat, change)
                result["changes"][stat] = actual_change
                result["stat_changes"][stat] = actual_change

    elif effect_type == "speed_modifier":
        # Modify speed for this turn
        speed_change = stats.get("speed", 0)
        result["changes"]["speed"] = speed_change
        result["stat_changes"]["speed"] = speed_change

        # May also apply wear
        if "engine_wear" in stats:
            actual_change = player_state.apply_stat_change("engine", -stats["engine_wear"])
            result["changes"]["engine"] = actual_change
            result["stat_changes"]["engine"] = actual_change

    elif effect_type == "opponent_speed_reduction":
        # Reduce opponent's speed
        speed_reduction = stats.get("speed_reduction", 1)
        result["changes"]["opponent_speed"] = -speed_reduction
        result["stat_changes"]["opponent_speed"] = -speed_reduction

    elif effect_type == "conditional_effect":
        # Effect depends on game state (e.g., "if trailing")
        condition = stats.get("condition")

        if condition == "if_trailing" and not player_state.is_leader:
            # Apply bonus if trailing
            if "speed" in stats:
                result["changes"]["speed"] = stats["speed"]
                result["stat_changes"]["speed"] = stats["speed"]
            if "engine_wear" in stats:
                actual_change = player_state.apply_stat_change("engine", -stats["engine_wear"])
                result["changes"]["engine"] = actual_change
                result["stat_changes"]["engine"] = actual_change

        elif condition == "if_leading" and player_state.is_leader:
            # Apply effect if leading
            if "opponent_speed_reduction" in stats:
                result["changes"]["opponent_speed"] = -stats["opponent_speed_reduction"]
                result["stat_changes"]["opponent_speed"] = -stats["opponent_speed_reduction"]

    elif effect_type == "dice_roll_effect":
        # Effect depends on dice roll
        roll = random.randint(1, 6)
        result["changes"]["dice_roll"] = roll

        success_threshold = stats.get("success_threshold", 4)
        if roll >= success_threshold:
            # Success
            if "success_speed" in stats:
                result["changes"]["speed"] = stats["success_speed"]
                result["stat_changes"]["speed"] = stats["success_speed"]
        else:
            # Failure
            if "failure_engine_wear" in stats:
                actual_change = player_state.apply_stat_change("engine", -stats["failure_engine_wear"])
                result["changes"]["engine"] = actual_change
                result["stat_changes"]["engine"] = actual_change

    elif effect_type == "reduce_engine_wear":
        # Reduce engine wear this turn (handled in speed calculation)
        reduction = stats.get("wear_reduction", 1)
        result["changes"]["wear_reduction"] = reduction

    elif effect_type == "draw_cards":
        # Draw additional cards
        count = stats.get("draw", 1)
        player_state.draw_cards(count)
        result["changes"]["cards_drawn"] = count

    # Also handle direct stat changes from card stats (for backwards compatibility with seed data)
    for stat in ["engine", "tires", "fuel", "reliability", "speed_modifier"]:
        if stat in stats and stat not in result["changes"]:
            if stat == "speed_modifier":
                result["stat_changes"]["speed"] = stats[stat]
            else:
                actual_change = target_state.apply_stat_change(stat, stats[stat])
                result["stat_changes"][stat] = actual_change

    return result


def validate_card_play(player_state, card_data: dict, phase: str) -> tuple:
    """Validate if a card can be played. Returns (is_valid, error_message)"""
    requirements = card_data.get("requirements", {})

    # Check phase
    card_type = card_data["card_type"]
    if phase == "strategy_selection" and card_type != "strategy":
        return False, "Can only play strategy cards in strategy phase"
    elif phase == "react" and card_type not in ["tactics", "event"]:
        return False, "Can only play tactics or event cards in react phase"

    # Check resources
    min_resources = requirements.get("min_resources", 0)
    if player_state.resources < min_resources:
        return False, f"Insufficient resources (need {min_resources}, have {player_state.resources})"

    # Check position requirements
    if requirements.get("requires_leader") and not player_state.is_leader:
        return False, "Must be the leader to play this card"

    if requirements.get("requires_trailing") and player_state.is_leader:
        return False, "Must be trailing to play this card"

    # Check stat requirements
    for stat, min_value in requirements.get("min_stats", {}).items():
        if player_state.car_stats.get(stat, 0) < min_value:
            return False, f"Insufficient {stat} (need {min_value}, have {player_state.car_stats.get(stat, 0)})"

    return True, None
