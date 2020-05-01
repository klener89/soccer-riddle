import random
from app.game import game
from flask import render_template, redirect, request, url_for, flash, Markup
from app.game.forms import SearchPlayerForm, SearchGameForm, SearchPlayerGameForm
from app.helpers.scrapers import find_mates, add_player
from app.helpers.utils import compare_players,render_level, replace_joker

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
    )


@game.route("play/<int:game_id>", methods=["GET", "POST"])
def play(game_id):
    from_name = request.args.get('from', "")
    to_name = request.args.get('to', "") 
    if not to_name:
        to_name= request.args.get('amp;to', "")
    if game_id==0:
        game = Game.query.order_by(func.random()).first()
        return redirect(url_for("game.play", game_id=game.id))
    else:
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
        player_validated = compare_players(player.name, form.search.data)
        if player_validated:
            return_player = player
            solved = True
            message = Markup("Congratulations! You found the right player. It's <a target='_blank' class='badge badge-pill badge-info' href='https://transfermarkt.com%s'>%s</a>" % (player.url, player.name))
            flash(message)
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
        from_name=from_name,
        to_name=to_name,
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
        flash("Congratulation, you created a new game")
        return redirect(url_for("game.share", game_id=game.id))
    return render_template("games/game_select_mates.html", player=player, mates=mates)

@game.route("/share/<int:game_id>/")
def share(game_id):
    game = Game.query.get(int(game_id))
    if not game:
        flash("Sorry the game could not be found")
        redirect(url_for("game.index"))
    return render_template("games/share.html", game=game)