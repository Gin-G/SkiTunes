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
    tracks = ski_movie_song_info.query.all()
    return render_template('home.html', tracks = tracks)

@app.route('/new_entry', methods=['GET', 'POST'])
def new_entry():
    if request.method == 'POST':
        if not request.form['song_name']:
            flash('Please enter all the fields', 'error')
        else:
            movie_song_info = ski_movie_song_info(song_name = request.form['song_name'], song_artist = request.form['song_artist'], skier_name = request.form['skier_name'], movie_name = request.form['movie_name'], ski_type = request.form['ski_type'], video_link = request.form['video_link'])
            db.session.add(movie_song_info)
            db.session.commit()

            flash('Record was successfully added')
            return redirect(url_for('home'))
    return render_template('new_entry.html')

@app.route('/bulkImport', methods=['GET', 'POST'])
def bulk_import():
    json_playlist = open('playlist.json')
    json_playlist = json.load(json_playlist)
    for track in json_playlist:
        track_name = track['track']['name']
        track_id = track['track']['id']
        song_artist = track['track']['artists'][0]['name']
        skier_name = movie_name = ski_type = video_link = None
        movie_song_info = ski_movie_song_info(song_name = track_name, song_artist = song_artist, spotify_id = track_id, skier_name = skier_name, movie_name = movie_name, ski_type = ski_type, video_link = video_link)
        db.session.add(movie_song_info)
        db.session.commit()
    return jsonify(json_playlist)
