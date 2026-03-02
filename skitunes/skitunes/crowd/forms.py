from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Optional


class SuggestEntryForm(FlaskForm):
    song_name = StringField('Song Name', validators=[DataRequired()])
    song_artist = StringField('Artist', validators=[Optional()])
    song_album = StringField('Album', validators=[Optional()])
    song_num = StringField('Song Number', validators=[Optional()])
    genres = StringField('Genres', validators=[Optional()])
    spotify_id = StringField('Spotify Link', validators=[Optional()])
    skier_name = StringField('Skier Name(s)', validators=[Optional()])
    ski_type = StringField('Primary Ski Style', validators=[Optional()])
    location = StringField('Location', validators=[Optional()])
    video_link = StringField('Segment Link', validators=[Optional()])
    movie_name = StringField('Movie Name', validators=[DataRequired()])
    movie_year = StringField('Movie Year', validators=[DataRequired()])
    movie_co = StringField('Production Company', validators=[DataRequired()])
    submit = SubmitField('Suggest Entry')


class ActionForm(FlaskForm):
    submit = SubmitField('Submit')
