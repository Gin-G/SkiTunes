from skitunes import db

class ski_movie_song_info(db.Model):
    __tablename__ = 'Ski Movie Tunes Info'
    song_name = db.Column('Song Title', db.String(100), primary_key = True)
    song_artist = db.Column('Song Artist', db.String(100))
    spotify_id = db.Column('Spotify ID', db.String(100))
    skier_name = db.Column('Skier Name', db.String(100))
    movie_name = db.Column('Movie Title', db.String(100))
    ski_type = db.Column('Primary Ski Style', db.String(100))
    video_link = db.Column('Link to segment', db.String(100))

    def __init__(self, song_name, song_artist, spotify_id, skier_name, movie_name, ski_type, video_link):
        self.song_name = song_name
        self.song_artist = song_artist
        self.spotify_id = spotify_id
        self.skier_name = skier_name
        self.movie_name = movie_name
        self.ski_type = ski_type
        self.video_link = video_link