"""WebSocket in-game event handlers"""
from flask_socketio import emit
from flask_login import current_user


def register_events(socketio):
    """Register game-related events"""

    @socketio.on('select_strategy_card')
    def handle_select_strategy(data):
        """Player selects their strategy card"""
        from app.game_engine import GameManager
        from app.game_engine.validators import validate_strategy_selection

        if not current_user.is_authenticated:
            emit('error', {'message': 'Not authenticated'})
            return

        player_id = current_user.id
        card_id = data.get('card_id')

        manager = GameManager()
        game_room = manager.get_player_game(player_id)

        if not game_room:
            emit('error', {'message': 'No active game'})
            return

        # Validate selection
        is_valid, error_msg = validate_strategy_selection(
            game_room, player_id, card_id)
        if not is_valid:
            emit('error', {'message': error_msg})
            return

        # Store selection (hidden until both ready)
        success = game_room.select_strategy_card(player_id, card_id)

        if success:
            emit('strategy_selected', {'card_id': card_id})
        else:
            emit('error', {'message': 'Failed to select card'})

    @socketio.on('ready_for_reveal')
    def handle_ready_for_reveal():
        """Player is ready to reveal strategy cards"""
        from app.game_engine import GameManager

        if not current_user.is_authenticated:
            emit('error', {'message': 'Not authenticated'})
            return

        player_id = current_user.id

        manager = GameManager()
        game_room = manager.get_player_game(player_id)

        if not game_room:
            emit('error', {'message': 'No active game'})
            return

        # Mark player as ready
        reveal_results = game_room.ready_for_reveal(player_id)

        if reveal_results:
            # Enhance results with player names for better UI display
            from app.models import User

            for pid in reveal_results.keys():
                user = User.query.get(pid)
                if user:
                    reveal_results[pid]['player_name'] = user.username

            # Both players ready, broadcast reveal
            socketio.emit(
                'strategy_reveal', reveal_results,
                room=f"game_{game_room.match_id}")

            # Send updated game state to both players individually
            for pid in [game_room.player1_id, game_room.player2_id]:
                state = game_room.get_sanitized_state(pid)
                socketio.emit(
                    'game_state_update', state,
                    room=f"player_{pid}")

    @socketio.on('play_tactic')
    def handle_play_tactic(data):
        """Play a tactic card during react phase"""
        from app.game_engine import GameManager
        from app.game_engine.validators import validate_tactic_play

        if not current_user.is_authenticated:
            emit('error', {'message': 'Not authenticated'})
            return

        player_id = current_user.id
        card_id = data.get('card_id')
        target = data.get('target', 'self')

        manager = GameManager()
        game_room = manager.get_player_game(player_id)

        if not game_room:
            emit('error', {'message': 'No active game'})
            return

        # Validate tactic play
        is_valid, error_msg = validate_tactic_play(
            game_room, player_id, card_id)
        if not is_valid:
            emit('error', {'message': error_msg})
            return

        try:
            # Play the tactic card
            effect_result = game_room.play_tactic_card(
                player_id, card_id, target)

            # Broadcast tactic played event with enhanced details
            from app.models import User
            user = User.query.get(player_id)

            socketio.emit('tactic_played', {
                'player_id': player_id,
                'player_name': user.username if user else 'Player',
                'card_id': card_id,
                'effect': effect_result
            }, room=f"game_{game_room.match_id}")

            # Send updated game state to both players individually
            for pid in [game_room.player1_id, game_room.player2_id]:
                state = game_room.get_sanitized_state(pid)
                socketio.emit(
                    'game_state_update', state,
                    room=f"player_{pid}")

        except ValueError as e:
            emit('error', {'message': str(e)})

    @socketio.on('pass_react_phase')
    def handle_pass_react():
        """Player passes their react phase turn"""
        from app.game_engine import GameManager

        if not current_user.is_authenticated:
            emit('error', {'message': 'Not authenticated'})
            return

        player_id = current_user.id

        manager = GameManager()
        game_room = manager.get_player_game(player_id)

        if not game_room:
            emit('error', {'message': 'No active game'})
            return

        # Pass react phase
        speed_results = game_room.pass_react_phase(player_id)

        # Notify about the pass
        socketio.emit(
            'player_passed', {'player_id': player_id},
            room=f"game_{game_room.match_id}")

        if speed_results:
            # Both passed, speed phase executed
            socketio.emit(
                'speed_phase_results', speed_results,
                room=f"game_{game_room.match_id}")

            # Check for lap completion
            for pid in [game_room.player1_id, game_room.player2_id]:
                player_state = game_room.player_states[pid]
                if f"{pid}_lap_completion" in speed_results:
                    # Handle multiple lap completions
                    laps_data = speed_results[f"{pid}_lap_completion"]
                    if isinstance(laps_data, list):
                        for lap_result in laps_data:
                            socketio.emit('lap_completed', {
                                'player_id': pid,
                                'lap': lap_result['lap'],
                                'completion_data': lap_result
                            }, room=f"game_{game_room.match_id}")
                    else:
                        # Backwards compatibility with old single-lap format
                        socketio.emit(
                            'lap_completed', {
                                'player_id': pid,
                                'lap': player_state.current_lap,
                                'completion_data': laps_data
                            }, room=f"game_{game_room.match_id}")

            # Check for game over
            if 'game_over' in speed_results:
                socketio.emit(
                    'game_over', speed_results['game_over'],
                    room=f"game_{game_room.match_id}")
                manager.remove_game(game_room.match_id)
                return

        # Send updated game state to both players individually
        for pid in [game_room.player1_id, game_room.player2_id]:
            state = game_room.get_sanitized_state(pid)
            socketio.emit(
                'game_state_update', state,
                room=f"player_{pid}")

    @socketio.on('request_game_state')
    def handle_request_state():
        """Request current game state"""
        from app.game_engine import GameManager

        if not current_user.is_authenticated:
            emit('error', {'message': 'Not authenticated'})
            return

        player_id = current_user.id

        manager = GameManager()
        game_room = manager.get_player_game(player_id)

        if not game_room:
            emit('error', {'message': 'No active game'})
            return

        state = game_room.get_sanitized_state(player_id)
        emit('game_state_update', state)

    @socketio.on('pit_stop')
    def handle_pit_stop(data):
        """Handle pit stop request"""
        from app.game_engine import GameManager
        from app.game_engine.validators import validate_pit_stop

        if not current_user.is_authenticated:
            emit('error', {'message': 'Not authenticated'})
            return

        player_id = current_user.id
        pit_type = data.get('pit_type', 'normal')

        manager = GameManager()
        game_room = manager.get_player_game(player_id)

        if not game_room:
            emit('error', {'message': 'No active game'})
            return

        player_state = game_room.player_states[player_id]

        # Validate pit stop
        is_valid, error_msg = validate_pit_stop(player_state, pit_type)
        if not is_valid:
            emit('error', {'message': error_msg})
            return

        # Perform pit stop
        success = player_state.pit_stop(pit_type)

        if success:
            socketio.emit('pit_stop_complete', {
                'player_id': player_id,
                'pit_type': pit_type
            }, room=f"game_{game_room.match_id}")

            # Send updated game state to both players individually
            for pid in [game_room.player1_id, game_room.player2_id]:
                state = game_room.get_sanitized_state(pid)
                socketio.emit(
                    'game_state_update', state,
                    room=f"player_{pid}")
        else:
            emit('error', {'message': 'Pit stop failed'})
