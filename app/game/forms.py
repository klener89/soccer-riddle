from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from wtforms.fields.html5 import IntegerField

class SearchPlayerForm(FlaskForm):
    search = StringField("Search for your Player", validators=[DataRequired()])
    submit = SubmitField("Search")

class SearchPlayerGameForm(FlaskForm):
    search = StringField("Search for your Player", validators=[DataRequired()])
    submit = SubmitField("Search")
        
class SearchGameForm(FlaskForm):
    search = IntegerField("Search for a specific game ID")
    submit = SubmitField("Search")
