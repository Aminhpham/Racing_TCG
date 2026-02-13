"""WebSocket matchmaking and lobby handlers"""
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from datetime import datetime


def register_events(socketio):
    """Register matchmaking-related events"""

    @socketio.on('create_lobby')
    def handle_create_lobby(data):
        """Create a new game lobby"""
        from app.models import Lobby, Deck
        from app import db

        if not current_user.is_authenticated:
            emit('error', {'message': 'Not authenticated'})
            return

        deck_id = data.get('deck_id')
        lobby_name = data.get('lobby_name', f"{current_user.username}'s Game")
        is_private = data.get('is_private', False)
        password = data.get('password')

        # Validate deck ownership
        deck = Deck.query.get(deck_id)
        if not deck or deck.user_id != current_user.id:
            emit('error', {'message': 'Invalid deck'})
            return

        # Validate deck has 40 cards
        if not deck.card_ids or len(deck.card_ids) != 40:
            emit('error', {'message': 'Deck must have exactly 40 cards'})
            return

        # Create lobby
        lobby = Lobby(
            host_id=current_user.id,
            host_deck_id=deck_id,
            name=lobby_name,
            is_private=is_private,
            password=password if is_private else None
        )
        db.session.add(lobby)
        db.session.commit()

        # Join lobby room
        join_room(f"lobby_{lobby.id}")

        emit('lobby_created', {
            'lobby': lobby_to_dict(lobby)
        })

        # Broadcast updated lobby list
        socketio.emit('lobby_list_update', {
            'lobbies': get_open_lobbies()
        }, )

    @socketio.on('join_lobby')
    def handle_join_lobby(data):
        """Join an existing lobby and start game"""
        from app.models import Lobby, GameMatch, Deck
        from app.game_engine import GameManager
        from app import db

        if not current_user.is_authenticated:
            emit('error', {'message': 'Not authenticated'})
            return

        lobby_id = data.get('lobby_id')
        deck_id = data.get('deck_id')
        password = data.get('password')

        lobby = Lobby.query.get(lobby_id)
        if not lobby or lobby.status != 'open':
            emit('error', {'message': 'Lobby not available'})
            return

        if lobby.is_private and lobby.password != password:
            emit('error', {'message': 'Incorrect password'})
            return

        # Validate deck
        deck = Deck.query.get(deck_id)
        if not deck or deck.user_id != current_user.id or len(deck.card_ids) != 40:
            emit('error', {'message': 'Invalid deck'})
            return

        # Create game match
        match = GameMatch(
            player1_id=lobby.host_id,
            player2_id=current_user.id,
            player1_deck_id=lobby.host_deck_id,
            player2_deck_id=deck_id,
            status='active',
            started_at=datetime.utcnow()
        )
        db.session.add(match)
        db.session.commit()

        # Update lobby status
        lobby.status = 'in_progress'
        db.session.commit()

        # Join lobby room
        join_room(f"lobby_{lobby_id}")

        # Notify both players game is starting
        socketio.emit('game_starting', {
            'match_id': match.id,
            'opponent': {
                'id': lobby.host_id,
                'username': lobby.host.username
            }
        }, room=f"lobby_{lobby_id}")

        # Create game room in GameManager
        manager = GameManager()
        host_deck = Deck.query.get(lobby.host_deck_id)

        # TODO: Get car data for both players (for now use default)
        default_car = {
            "engine": 8,
            "tires": 6,
            "fuel": 6,
            "reliability": 3,
            "ability": ""
        }

        game_room = manager.create_game(
            match.id,
            lobby.host_id,
            current_user.id,
            default_car,  # Player 1 car
            default_car,  # Player 2 car
            host_deck.card_ids,
            deck.card_ids
        )

        # Both players join game room (player rooms joined on connect)
        join_room(f"game_{match.id}")

        # Send initial game state to both players individually
        for player_id in [lobby.host_id, current_user.id]:
            state = game_room.get_sanitized_state(player_id)
            socketio.emit('game_state_update', state, room=f"player_{player_id}")

        # Clean up lobby
        db.session.delete(lobby)
        db.session.commit()

        # Broadcast updated lobby list
        socketio.emit('lobby_list_update', {
            'lobbies': get_open_lobbies()
        }, )

    @socketio.on('leave_lobby')
    def handle_leave_lobby(data):
        """Leave a lobby"""
        from app.models import Lobby
        from app import db

        if not current_user.is_authenticated:
            return

        lobby_id = data.get('lobby_id')
        lobby = Lobby.query.get(lobby_id)

        if lobby and lobby.host_id == current_user.id:
            # Host is leaving, delete lobby
            db.session.delete(lobby)
            db.session.commit()

            leave_room(f"lobby_{lobby_id}")

            # Broadcast updated lobby list
            socketio.emit('lobby_list_update', {
                'lobbies': get_open_lobbies()
            }, )

    @socketio.on('list_lobbies')
    def handle_list_lobbies():
        """Get list of open lobbies"""
        emit('lobby_list_update', {
            'lobbies': get_open_lobbies()
        })


def lobby_to_dict(lobby) -> dict:
    """Convert lobby to dictionary"""
    return {
        'id': lobby.id,
        'name': lobby.name,
        'host': {
            'id': lobby.host.id,
            'username': lobby.host.username
        },
        'is_private': lobby.is_private,
        'status': lobby.status,
        'created_at': lobby.created_at.isoformat()
    }


def get_open_lobbies() -> list:
    """Get list of open lobbies"""
    from app.models import Lobby

    lobbies = Lobby.query.filter_by(status='open').all()
    return [lobby_to_dict(lobby) for lobby in lobbies]
