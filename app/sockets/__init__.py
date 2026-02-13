"""Socket.IO event handlers registration"""


def register_socket_events(socketio):
    """Register all SocketIO event handlers"""
    from . import connection_events
    from . import matchmaking_events
    from . import game_events

    # Register connection events
    connection_events.register_events(socketio)

    # Register matchmaking events
    matchmaking_events.register_events(socketio)

    # Register game events
    game_events.register_events(socketio)
