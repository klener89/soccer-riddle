import sqlalchemy as sa

from app import db

class Player(db.Model):
    __tablename__ = "t_players"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    player_id = sa.Column(sa.Integer, unique=True, index=True, nullable=True)
    name = sa.Column(sa.String, nullable=True)
    club_id = sa.Column(sa.Integer, nullable=True)
    club = sa.Column(sa.String, nullable=True)
    club_img = sa.Column(sa.String, nullable=True)
    img = sa.Column(sa.String, nullable=True)
    url = sa.Column(sa.String, nullable=True)
    age = sa.Column(sa.Integer, nullable=True)
    position = sa.Column(sa.String, nullable=True)
    nationality = sa.Column(sa.String, nullable=True)
    nationality_img = sa.Column(sa.String, nullable=True)
