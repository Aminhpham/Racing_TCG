from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Deck, GameMatch

matchmaking_bp = Blueprint("matchmaking", __name__, url_prefix="/matchmaking")


@matchmaking_bp.route("/")
@login_required
def lobby_browser():
    """Render the lobby browser page"""
    decks = Deck.query.filter_by(user_id=current_user.id).all()
    return render_template("matchmaking/lobby_browser.html", decks=decks)


@matchmaking_bp.route("/game/<int:match_id>")
@login_required
def game_room(match_id):
    """Render the game room UI"""
    match = GameMatch.query.get_or_404(match_id)

    # Verify player is part of this match
    if current_user.id not in [match.player1_id, match.player2_id]:
        return redirect(url_for('matchmaking.lobby_browser'))

    return render_template("matchmaking/game_room.html", match_id=match_id, match=match)
