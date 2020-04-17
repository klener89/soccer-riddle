from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SearchPlayerForm(FlaskForm):
    search = StringField("Search for your Player", validators=[DataRequired()])
    submit = SubmitField("Search")