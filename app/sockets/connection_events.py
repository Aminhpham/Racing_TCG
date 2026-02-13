"""WebSocket connection and disconnection handlers"""
from flask_socketio import emit, join_room, disconnect
from flask_login import current_user
from flask import request
import threading

# Track disconnect timers
disconnect_timers = {}


def register_events(socketio):
    """Register connection-related events"""

    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        if not current_user.is_authenticated:
            return False  # Reject unauthenticated connections

        player_id = current_user.id

        # Always join player-specific room for receiving personal game states
        join_room(f"player_{player_id}")

        # Cancel any existing disconnect timer
        if player_id in disconnect_timers:
            disconnect_timers[player_id].cancel()
            del disconnect_timers[player_id]

        # Check for active game
        from app.game_engine import GameManager
        manager = GameManager()
        game_room = manager.get_player_game(player_id)

        if game_room:
            # Reconnection to active game
            game_room.connected_players[player_id] = True
            join_room(f"game_{game_room.match_id}")

            # Send current state
            state = game_room.get_sanitized_state(player_id)
            emit('game_state_update', state)

            # Notify opponent of reconnection
            opponent_id = game_room.get_opponent_id(player_id)
            emit('player_reconnected',
                 {'player_id': player_id, 'username': current_user.username},
                 room=f"game_{game_room.match_id}",
                 skip_sid=request.sid)

        # Send connection confirmation
        emit('connection_established', {
            'user_id': player_id,
            'username': current_user.username,
            'active_game': game_room.match_id if game_room else None
        })

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        if not current_user.is_authenticated:
            return

        player_id = current_user.id

        from app.game_engine import GameManager
        manager = GameManager()
        game_room = manager.get_player_game(player_id)

        if game_room and not game_room.game_over:
            # Mark player as disconnected
            game_room.connected_players[player_id] = False

            # Notify opponent
            emit('player_disconnected', {
                'player_id': player_id,
                'username': current_user.username,
                'timeout_seconds': 60
            }, room=f"game_{game_room.match_id}")

            # Start 60-second disconnect timer
            timer = threading.Timer(60.0, handle_disconnect_timeout,
                                   args=[game_room.match_id, player_id])
            timer.start()
            disconnect_timers[player_id] = timer


def handle_disconnect_timeout(match_id: int, player_id: int):
    """Handle player disconnect timeout (forfeit game)"""
    from app.game_engine import GameManager
    from app import socketio

    manager = GameManager()
    game_room = manager.get_game(match_id)

    if game_room and not game_room.connected_players[player_id]:
        # Player didn't reconnect, forfeit game
        opponent_id = game_room.get_opponent_id(player_id)
        game_room.end_game(opponent_id, "opponent_disconnect")

        socketio.emit('game_over', {
            'winner_id': opponent_id,
            'condition': 'opponent_disconnect',
            'message': 'Opponent disconnected'
        }, room=f"game_{match_id}")

        # Clean up
        manager.remove_game(match_id)
        if player_id in disconnect_timers:
            del disconnect_timers[player_id]
