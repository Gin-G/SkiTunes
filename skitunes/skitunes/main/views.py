from crypt import methods
from textwrap import indent

from flask import request, flash, redirect, url_for, jsonify
from matplotlib.font_manager import json_load
from skitunes import app, db
from skitunes.spotify.models import ski_movie_song_info
from flask.templating import render_template
import json

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/fahrtbags')
def fart():
    return render_template('fahrtbags.html')

@app.route('/fahrtbags/one-piece')
def one_piece():
    return render_template('one-piece.html')

@app.route('/fahrtbags/about')
def about_fart():
    return render_template('about.html')

@app.route('/skitunes')
def skitunes():
    tracks = ski_movie_song_info.query.all()
    return render_template('skitunes.html', tracks = tracks)

@app.route('/skitunes/skibase')
def skibase():
    tracks = ski_movie_song_info.query.all()
    return render_template('skibase.html', tracks = tracks)

@app.route('/skitunes/skibase_lite')
def skibase_lite():
    tracks = ski_movie_song_info.query.all()
    return render_template('skibase_lite.html', tracks = tracks)

@app.route('/skitunes/findmovie')
def findmovie():
    song_name = request.args.get('song_name')
    song_artist = request.args.get('song_artist')
    print(song_name,song_artist)
    if len(song_artist) == 0:
        filter_info = ski_movie_song_info.query.filter(ski_movie_song_info.song_name.like(song_name))
    elif len(song_name) == 0:
        filter_info = ski_movie_song_info.query.filter(ski_movie_song_info.song_artist.like(song_artist))
    else:
        filter_info = ski_movie_song_info.query.filter(ski_movie_song_info.song_name.like(song_name),ski_movie_song_info.song_artist.like(song_artist))
    return render_template('skibase.html', tracks = filter_info)

@app.route('/skitunes/filtermovie')
def filter_movie():
    movie_name = request.args.get("movie_name")
    filter_info = ski_movie_song_info.query.filter(ski_movie_song_info.movie_name == movie_name)
    return render_template('skibase.html', tracks = filter_info)

@app.route('/skitunes/filterskier')
def filter():
    skier_name = request.args.get('skier_name')
    filter_info = ski_movie_song_info.query.filter(ski_movie_song_info.skier_name == skier_name)
    return render_template('skibase.html', tracks = filter_info)

@app.route('/skitunes/filtersong')
def filter_song():
    song_name = request.args.get("song_name")
    filter_info = ski_movie_song_info.query.filter(ski_movie_song_info.song_name == song_name)
    return render_template('skibase.html', tracks = filter_info)

@app.route('/skitunes/filterartist')
def filter_artist():
    song_artist = request.args.get("song_artist")
    filter_info = ski_movie_song_info.query.filter(ski_movie_song_info.song_artist == song_artist)
    return render_template('skibase.html', tracks = filter_info)

@app.route('/skitunes/filteralbum')
def filter_album():
    song_album = request.args.get("song_album")
    filter_info = ski_movie_song_info.query.filter(ski_movie_song_info.song_album == song_album)
    return render_template('skibase.html', tracks = filter_info)

@app.route('/skitunes/filtermovieco')
def filter_movieco():
    movie_co = request.args.get("movie_co")
    filter_info = ski_movie_song_info.query.filter(ski_movie_song_info.movie_co == movie_co)
    return render_template('skibase.html', tracks = filter_info)

@app.route('/skitunes/filterlocation')
def filter_location():
    location = request.args.get("location")
    filter_info = ski_movie_song_info.query.filter(ski_movie_song_info.location == location)
    return render_template('skibase.html', tracks = filter_info)

@app.route('/skitunes/filtertype')
def filter_type():
    ski_type = request.args.get("ski_type")
    filter_info = ski_movie_song_info.query.filter(ski_movie_song_info.ski_type == ski_type)
    return render_template('skibase.html', tracks = filter_info)

@app.route('/skitunes/likewhat')
def like_what():
    return render_template('likewhat.html')

@app.route('/new_entry', methods=['GET', 'POST'])
def new_entry():
    if request.method == 'POST':
        if not request.form['song_name']:
            flash('Please enter all the fields', 'error')
        else:
            movie_song_info = ski_movie_song_info(song_name = request.form['song_name'], song_artist = request.form['song_artist'], song_album = request.form['song_album'], song_num=request.form['song_num'], spotify_id=request.form['spotify_link'], skier_name = request.form['skier_name'], movie_name = request.form['movie_name'], movie_year=request.form['movie_year'], movie_co=request.form['movie_co'], ski_type = request.form['ski_type'], location=request.form['location'], video_link = request.form['video_link'])           
            db.session.add(movie_song_info)
            db.session.commit()

            flash('Record was successfully added')
            return redirect(url_for('skitunes'))
    return render_template('new_entry.html')

@app.route('/bulkImport', methods=['GET', 'POST'])
def bulk_import():
    json_playlist = open('clean_data.json')
    json_playlist = json.load(json_playlist)
    for track in json_playlist:
        movie_name = track["Movie Name"]
        movie_year = track["Movie Year"]
        movie_co = track["Production Co."]
        song_num = track["Song Number"]
        song_artist = track["Artist"]
        song_name = track["Song Name"]
        song_album = track["Song Album"]
        spotify_link = track["Spotify Link"]
        ski_type = track["Skiing type"]
        skier_name = track["Skier Name(s)"]
        location = track["Location"]
        video_link  = 'Unknown'
        movie_song_info = ski_movie_song_info(song_name = song_name, song_artist = song_artist, song_album = song_album, song_num=song_num, spotify_id=spotify_link, skier_name = skier_name, movie_name = movie_name, movie_year=movie_year, movie_co=movie_co, ski_type = ski_type, location=location, video_link = video_link)
        db.session.add(movie_song_info)
        db.session.commit()
    return jsonify(json_playlist)
