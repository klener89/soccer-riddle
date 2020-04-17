from app.game import game
from flask import render_template, redirect, request, url_for, flash
from app.game.forms import SearchPlayerForm
from app.helpers.scrapers import find_player, find_mates, add_player

# from app.forms import *
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user,
    login_manager,
)

from app import db, login_manager
from app.models import User, Player, Game, LinkGamePlayer

################
#### routes ####
################


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@game.route("/")
def index():
    return redirect(url_for("game.find_game"))


@game.route("/<int:game_id>")
def play(game_id):
    return render_template("games/game_play.html", game_id=game_id)


@game.route("/find_game")
def find_game():
    return render_template("games/game_play.html")


@game.route("/create", methods=["GET", "POST"])
def create():
    form = SearchPlayerForm()
    if form.validate_on_submit():
        players = add_player(form.search.data)
        return render_template("games/game_create.html", form=form, results=players)
    if "player" in request.form:
        return redirect(url_for("game.add_mates", id=request.form["player"]))
    return render_template("games/game_create.html", form=form)


@game.route("/create/<int:id>/mates", methods=["GET", "POST"])
def add_mates(id):
    player = db.session.query(Player).filter(Player.player_id == id).first()
    if not player:
        flash("Sorry there was an error, the player could not be found in our database")
        return redirect(url_for("games.create"))
    mates = find_mates(id)
    if "mateSelect" in request.form:
        game = Game(level=request.form["inlineDifficulty"], user_game=True, player_id=id)
        db.session.add(game)
        db.session.flush()
        for item in request.form.getlist("mateSelect"):
            player = item.split(' - ',1)
            add_player(player[1])
            player_id = player[0]
            link = LinkGamePlayer(game_id=game.id, player_id=int(player_id))
            db.session.add(link)
        flash("Congratulation, you created the game with the ID %d" % game.id)
        print(game.id)
        return redirect(url_for("game.index"))
    return render_template("games/game_select_mates.html", player=player, mates=mates)
