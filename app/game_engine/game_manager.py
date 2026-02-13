from typing import Dict, Optional
from .game_room import GameRoom


class GameManager:
    """Singleton manager for all active game rooms"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.active_rooms: Dict[int, GameRoom] = {}
            cls._instance.player_to_room: Dict[int, int] = {}  # player_id -> match_id
        return cls._instance

    def create_game(self, match_id: int, player1_id: int, player2_id: int,
                    player1_car: dict, player2_car: dict,
                    player1_deck: list, player2_deck: list) -> GameRoom:
        """Create a new game room"""
        room = GameRoom(
            match_id,
            player1_id, player2_id,
            player1_car, player2_car,
            player1_deck, player2_deck
        )
        self.active_rooms[match_id] = room
        self.player_to_room[player1_id] = match_id
        self.player_to_room[player2_id] = match_id
        return room

    def get_game(self, match_id: int) -> Optional[GameRoom]:
        """Get active game room by match ID"""
        return self.active_rooms.get(match_id)

    def get_player_game(self, player_id: int) -> Optional[GameRoom]:
        """Get game room for a specific player"""
        match_id = self.player_to_room.get(player_id)
        return self.active_rooms.get(match_id) if match_id else None

    def remove_game(self, match_id: int):
        """Remove completed game from active rooms"""
        room = self.active_rooms.pop(match_id, None)
        if room:
            self.player_to_room.pop(room.player1_id, None)
            self.player_to_room.pop(room.player2_id, None)

    def persist_game_state(self, match_id: int):
        """Save current game state to database"""
        room = self.active_rooms.get(match_id)
        if room:
            room.save_to_db()

    def get_active_game_count(self) -> int:
        """Get number of active games"""
        return len(self.active_rooms)
