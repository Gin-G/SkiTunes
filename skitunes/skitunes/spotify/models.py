from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import relationship
from skitunes import db


class Movie(db.Model):
    __tablename__ = "movies"
    movie_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    movie_name = db.Column(db.String(200))
    movie_year = db.Column(db.String(10))
    movie_co = db.Column(db.String(200))
    movie_img_url = db.Column(db.String(500))
    songs = relationship("ski_movie_song_info", back_populates="movie")

    def __init__(self, movie_name, movie_year, movie_co, movie_img_url):
        self.movie_name = movie_name
        self.movie_year = movie_year
        self.movie_co = movie_co
        self.movie_img_url = movie_img_url


class ski_movie_song_info(db.Model):
    __tablename__ = 'songs'
    db_id = db.Column('id', Integer, primary_key=True, autoincrement=True)
    song_name = db.Column(db.String(200))
    song_artist = db.Column(db.String(200))
    song_album = db.Column(db.String(200))
    song_num = db.Column(db.String(50))
    genres = db.Column(db.String(500))
    spotify_id = db.Column(db.String(500))
    skier_name = db.Column(db.String(500))
    movie_id = db.Column(db.Integer, ForeignKey('movies.movie_id'))
    movie = relationship("Movie", back_populates="songs")
    ski_type = db.Column(db.String(200))
    location = db.Column(db.String(500))
    video_link = db.Column(db.String(500))

    def __init__(self, song_name, song_artist, song_album, song_num, genres,
                 spotify_id, skier_name, ski_type, location, video_link):
        self.song_name = song_name
        self.song_artist = song_artist
        self.song_album = song_album
        self.song_num = song_num
        self.genres = genres
        self.spotify_id = spotify_id
        self.skier_name = skier_name
        self.ski_type = ski_type
        self.location = location
        self.video_link = video_link

    def format(self):
        return {
            'id': self.db_id,
            'Song Name': self.song_name,
            'Song Artist': self.song_artist,
            'Song Album': self.song_album,
            'Genres': self.genres,
            'Skier Name': self.skier_name,
            'Movie Name': self.movie.movie_name if self.movie else None,
            'Production Company': self.movie.movie_co if self.movie else None,
            'Movie Year': self.movie.movie_year if self.movie else None,
            'Ski Type': self.ski_type,
            'Location': self.location,
        }
