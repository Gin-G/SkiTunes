# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import Optional, NumberRange
from datetime import datetime

class MovieSearchForm(FlaskForm):
    song_name = StringField('Song Name', 
        render_kw={"placeholder": "Song Name"})
    
    song_artist = StringField('Artist Name', 
        render_kw={"placeholder": "Artist Name"})
    
    movie_year = IntegerField('From Year',
        validators=[
            Optional(),
            NumberRange(min=1900, max=datetime.now().year, 
                message="Please enter a year between 1900 and present")
        ],
        render_kw={"placeholder": "From Year"})
    
    movie_year2 = IntegerField('To Year',
        validators=[
            Optional(),
            NumberRange(min=1900, max=datetime.now().year, 
                message="Please enter a year between 1900 and present")
        ],
        render_kw={"placeholder": "To Year"})
    
    submit = SubmitField('Search Movies')