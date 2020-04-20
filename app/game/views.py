import random
from app.game import game
from flask import render_template, redirect, request, url_for, flash
from app.game.forms import SearchPlayerForm, SearchGameForm, SearchPlayerGameForm
from app.helpers.scrapers import find_player, find_mates, add_player
from app.helpers.utils import render_level, replace_joker

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user,
    login_manager,
)

from app import db, login_manager
from app.models import User, Player, Game, LinkGamePlayer
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql.expression import func

################
#### routes ####
################


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@game.route("/", methods=["GET", "POST"])
@game.route("/<int:page>", methods=["GET", "POST"])
def index(page=1):
    form = SearchGameForm()
    demo_game = Game.query.get(16)
    random_game = Game.query.order_by(func.random()).first()
    try:
        games_list = Game.query.order_by(Game.id.asc()).paginate(page, per_page=5)
    except OperationalError:
        flash("No more games in the database.")
        games_list = None
    if form.validate_on_submit():
        game = Game.query.get(int(form.search.data))
        if not game:
            flash("Sorry, we could not find a game with this ID")
            return redirect(url_for("game.index"))
        return redirect(url_for("game.play", game_id=game.id))
    return render_template(
        "games/index.html",
        form=form,
        games_list=games_list,
        render_level=render_level,
        demo_game=demo_game,
        random_game_id=random_game.id,
    )


@game.route("play/<int:game_id>", methods=["GET", "POST"])
@game.route("play/<int:game_id>/<string:name>", methods=["GET", "POST"])
def play(game_id, name=""):
    game = Game.query.get(int(game_id))
    if not game:
        flash("Sorry the game could not be found")
        redirect(url_for("game.index"))
    player = db.session.query(Player).filter(Player.player_id == game.player_id).first()
    
    # Jokers
    joker_num =0
    if "joker" in request.form:
        joker_num = int(request.form["joker"])
        flash("We added more information to the player card")
    return_player = replace_joker(player, joker_num)
    form = SearchPlayerGameForm()
    solved = False
    if form.validate_on_submit():
        search_players = find_player(form.search.data)
        found_player = next(
            (item for item in search_players if int(item["id"]) == player.player_id),
            None,
        )
        if found_player:
            return_player = player
            solved = True
            flash("Congratulations! You found the right player. It's %s" % player.name)
        else:
            form.search.errors = (
                "Try again, %s is not your guy. Maybe your search was to unspecific as well"
                % form.search.data,
            )
    return render_template(
        "games/game_play.html",
        player=return_player,
        form=form,
        game=game,
        name=name,
        solved=solved,
        joker_count=joker_num + 1
    )


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
        game = Game(
            level=request.form["inlineDifficulty"], user_game=True, player_id=id
        )
        db.session.add(game)
        db.session.flush()
        for item in request.form.getlist("mateSelect"):
            player = item.split(" - ", 1)
            add_player(player[1])
            player_id = player[0]
            link = LinkGamePlayer(game_id=game.id, player_id=int(player_id))
            db.session.add(link)
        flash("Congratulation, you created the game with the ID %d" % game.id)
        print(game.id)
        return redirect(url_for("game.index"))
    return render_template("games/game_select_mates.html", player=player, mates=mates)
