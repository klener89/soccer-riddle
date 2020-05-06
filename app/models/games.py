import sqlalchemy as sa
import sqlalchemy.orm as orm

from enum import IntEnum
from app import db
from app.models.link_games_player import LinkGamePlayer


class EnumRole(IntEnum):
    easy = 5
    medium = 10
    hard = 20

class Game(db.Model):
    __tablename__ = "t_games"

    # columns
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    level = sa.Column(sa.Integer, default=10, nullable=True)
    player_id = sa.Column(sa.Integer, sa.ForeignKey("t_players.player_id"), nullable=False)
    user_game = sa.Column(sa.Boolean, default=False, nullable=False)
    num_solved = sa.Column(sa.Integer, default=0, nullable=True)
    num_played = sa.Column(sa.Integer, default=0, nullable=True)
    joker = sa.Column(sa.Boolean, server_default='true', nullable=False)
    # relationships
    games = orm.relationship("LinkGamePlayer", backref="game")
    players = orm.relationship("Player", secondary=LinkGamePlayer.__table__)