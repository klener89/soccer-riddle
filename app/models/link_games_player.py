import datetime as dt
import sqlalchemy as sa
from app import db

class LinkGamePlayer(db.Model):
    __tablename__ = "t_link_games_player"

    # columns
    game_id = sa.Column(sa.Integer, sa.ForeignKey("t_games.id"), nullable=False, primary_key=True)
    player_id = sa.Column(sa.Integer, sa.ForeignKey("t_players.player_id"), nullable=False, primary_key=True)

    __table_args__ = tuple([sa.UniqueConstraint("game_id", "player_id", name="uix_game_id_player_id_1")])