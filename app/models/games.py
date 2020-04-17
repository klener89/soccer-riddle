import sqlalchemy as sa

from enum import IntEnum
from app import db

class EnumRole(IntEnum):
    Easy = 5
    MEDIUM = 10
    HARD = 20

class Game(db.Model):
    __tablename__ = "t_games"

    # columns
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    level = sa.Column(sa.Integer, default=10, nullable=True)
    player_id = sa.Column(sa.Integer, sa.ForeignKey("t_players.player_id"), nullable=False, primary_key=True)
    user_game = sa.Column(sa.Boolean, default=False, nullable=False)
    num_solved = sa.Column(sa.Integer, default=0, nullable=True)
