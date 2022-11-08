from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import relationship
from skitunes import db

class ski_movie_song_info(db.Model):
    __tablename__ = 'Ski Movie Tunes Info'
    db_id = db.Column('id', Integer, primary_key = True)
    song_name = db.Column('Song Title', db.String(100))
    song_artist = db.Column('Song Artist', db.String(100))
    song_album = db.Column('Album', db.String(100))
    song_num = db.Column('Song Number', db.String(100))
    spotify_id = db.Column('Spotify Link', db.String(100))
    skier_name = db.Column('Skier Name', db.String(100))
    movie_details = relationship("Movie", back_populates="parent")
    ski_type = db.Column('Primary Ski Style', db.String(100))
    location = db.Column('Location', db.String(100))
    video_link = db.Column('Link to segment', db.String(100))

    def __init__(self, song_name, song_artist, song_album, song_num, spotify_id, skier_name, ski_type, location, video_link):
        self.song_name = song_name
        self.song_artist = song_artist
        self.song_album = song_album
        self.song_num = song_num
        self.spotify_id = spotify_id
        self.skier_name = skier_name
        self.ski_type = ski_type
        self.location = location
        self.video_link = video_link

    def format(self):
        return {
            'id':self.db_id,
            'Song Name':self.song_name,
            'Song Artist':self.song_artist,
            'Song Album':self.song_album,
            'Skier Name':self.skier_name,
            'Movie Name':self.movie_name,
            'Production Company':self.movie_co,
            'Movie Year':self.movie_year,
            'Ski Type':self.ski_type,
            'Location':self.location,
        }

class Movie(db.Model):
    __tablename__ = "movie_details"
    movie_id = db.Column('movie_id', Integer, primary_key = True) 
    movie_name = db.Column('Movie Name', db.String(100))
    movie_year = db.Column('Movie Year', db.String(100))
    movie_co = db.Column('Production Company', db.String(100))
    movie_img_url = db.Column('Movie Cover URL', db.String(100))
    parent_id = db.Column(db.Integer, ForeignKey(ski_movie_song_info.db_id))
    parent = relationship("ski_movie_song_info", back_populates="movie_details")

    def __init__(self, movie_name, movie_year, movie_co, movie_img_url):
        self.movie_name = movie_name
        self.movie_year = movie_year
        self.movie_co = movie_co
        self.movie_img_url = movie_img_url
