from .card_effects import get_card_data


def validate_strategy_selection(game_room, player_id: int, card_id: int) -> tuple:
    """Validate strategy card selection. Returns (is_valid, error_message)"""
    if game_room.current_phase != "strategy_selection":
        return False, "Not in strategy selection phase"

    player_state = game_room.player_states.get(player_id)
    if not player_state:
        return False, "Invalid player"

    if card_id not in player_state.hand:
        return False, "Card not in hand"

    card_data = get_card_data(card_id)
    if card_data["card_type"] != "strategy":
        return False, "Must select a strategy card"

    return True, None


def validate_tactic_play(game_room, player_id: int, card_id: int) -> tuple:
    """Validate tactic card play. Returns (is_valid, error_message)"""
    if game_room.current_phase != "react":
        return False, "Not in react phase"

    if game_room.active_player_id != player_id:
        return False, "Not your turn"

    player_state = game_room.player_states.get(player_id)
    if not player_state:
        return False, "Invalid player"

    if card_id not in player_state.hand:
        return False, "Card not in hand"

    card_data = get_card_data(card_id)
    if card_data["card_type"] not in ["tactics", "event"]:
        return False, "Not a valid card for react phase"

    # Check requirements
    requirements = card_data.get("requirements", {})

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
            return False, f"Insufficient {stat} (need {min_value})"

    return True, None


def validate_pit_stop(player_state, pit_type: str = "normal") -> tuple:
    """Validate pit stop request. Returns (is_valid, error_message)"""
    if pit_type == "normal" and player_state.resources < 2:
        return False, "Need 2 resources for normal pit stop"
    elif pit_type == "fast" and player_state.resources < 1:
        return False, "Need 1 resource for fast pit stop"
    elif pit_type == "full" and player_state.resources < 3:
        return False, "Need 3 resources for full service"

    return True, None
