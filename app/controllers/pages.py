from flask import render_template, Blueprint, request
from app.forms import *
from flask_login import login_user, logout_user, login_required, current_user

blueprint = Blueprint('pages', __name__)

from app import db, login_manager
from app.models import User

################
#### routes ####
################

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@blueprint.route('/')
def home():
    return render_template('pages/placeholder.home.html')


@blueprint.route('/about')
def about():
    return render_template('pages/placeholder.about.html')


@blueprint.route('/login')
def login():
    form = LoginForm(request.form)
    return render_template('forms/login.html', form=form)


@blueprint.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form=form)


@blueprint.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form=form)
