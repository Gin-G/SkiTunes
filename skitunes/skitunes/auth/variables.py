import os 


GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = ("https://accounts.google.com/.well-known/openid-configuration")

FLASK_DEBUG = os.environ.get("FLASK_DEBUG",True)
if FLASK_DEBUG:
    google_redirect_uri_url = "http://127.0.0.1:5000/login/callback"
    spotify_redirect_uri_url = "http://127.0.0.1:5000/spotify/login/q"
else:
    google_redirect_uri_url = "https://www.skimoviesongs.com/login/callback"
    spotify_redirect_uri_url = "https://www.skimoviesongs.com/spotify/login/q"

SPOTIFY_AUTH_BASE_URL = "https://accounts.spotify.com/{}"
SPOTIFY_AUTH_URL = SPOTIFY_AUTH_BASE_URL.format('authorize')
SCOPE = "playlist-modify-public playlist-modify-private user-read-recently-played user-top-read"
client_id = os.environ.get("SPOTIFY_CLIENT_ID", None)