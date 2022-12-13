from crypt import methods
from textwrap import indent

from flask import request, flash, redirect, url_for, jsonify, send_file, session
from flask_login import current_user, LoginManager, login_required, login_user, logout_user
from matplotlib.font_manager import json_load
from skitunes import app, db
from skitunes.spotify.models import ski_movie_song_info, Movie
from skitunes.spotify.functions import create_playlist, add_tracks
from flask.templating import render_template
import requests
import os
import json


@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def home():
    if current_user.is_authenticated:
        name = current_user.name
        profile_pic = current_user.profile_pic
        return render_template('skitunes.html', name=name, profile_pic=profile_pic)
    else:
        return redirect(url_for('skitunes'))

@app.route('/account')
@login_required
def account():
    return render_template('account.html')

@app.route('/templates/header.html')
def header():
    return render_template('header.html')

@app.route('/static/Logo.png')
def logo():
    filename = 'static/Logo.png'
    return send_file(filename)

@app.route('/templates/navbar.html')
def navbar():
    tracks = db.session.query(Movie.movie_co).all()
    track_list = []
    for track in tracks:
        track = str(track)
        track = track.replace("',","")
        track = track.replace('",',"")
        track = track.replace(')',"")
        track = track.replace('"',"")
        track = track.replace("('","")
        track = track.replace('("',"")
        if track not in track_list:
            track_list.append(track)
    track_list.sort()
    return render_template('navbar.html', tracks = track_list)

@app.route('/templates/create_playlist.html')
def create_playlist():
    return render_template('create_playlist.html')

@app.route('/skitunes')
def skitunes():
    tracks = ski_movie_song_info.query.all()
    return render_template('skitunes.html', tracks = tracks)

@app.route('/skitunes/skibase')
@login_required
def skibase():
    tracks = ski_movie_song_info.query.all()
    return render_template('skibase.html', tracks = tracks)

@app.route('/skitunes/skibase/movie/company/<name>')
@login_required
def prod_co(name):
    movie_co = db.session.query(Movie).filter(Movie.movie_co == name).all()
    prod_list = []
    for id in movie_co:
        filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.db_id.contains(id.parent_id)).all()
        prod_list.append(filter_info)
    return render_template('movie_co.html', movie_co = prod_list)

@app.route('/skitunes/skibase/movie/year/<year>')
@login_required
def year(year):
    movie_year = db.session.query(Movie).filter(Movie.movie_year == year).all()
    year_list = []
    for id in movie_year:
        filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.db_id.contains(id.parent_id)).all()
        year_list.append(filter_info)
    return render_template('movie_year.html', movie_year = year_list)

@app.route('/skitunes/skibase/movie/<name>')
@login_required
def ski_movie(name):
    movie_info = db.session.query(Movie).filter(Movie.movie_name.contains(name)).all()
    movie_co = db.session.query(Movie).filter(Movie.movie_name.contains(name)).first()
    track_list = []
    for id in movie_info:
        filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.db_id.contains(id.parent_id)).all()
        track_list.append(filter_info)
    return render_template('movie_info.html', movie_info = track_list, movie_name = str(name), movie_co = movie_co)

@app.route('/skitunes/skibase_lite')
@login_required
def skibase_lite():
    tracks = ski_movie_song_info.query.all()
    return render_template('skibase_lite.html', tracks = tracks)

@app.route('/skitunes/findmovie')
def findmovie():
    song_name = request.args.get('song_name')
    song_artist = request.args.get('song_artist')
    movie_year = request.args.get('movie_year')
    if len(song_artist) != 0:
        if len(song_name) != 0:
            filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.song_name.contains(song_name),ski_movie_song_info.song_artist.contains(song_artist)).all()
            return render_template('skibase.html', tracks = filter_info)
        else:
            filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.song_artist.contains(song_artist)).all()
        return render_template('skibase.html', tracks = filter_info)
    elif len(song_name) != 0:
        filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.song_name.contains(song_name)).all()
        return render_template('skibase.html', tracks = filter_info)
    elif len(movie_year) != 0:
        movie_filter_info = db.session.query(Movie).filter(Movie.movie_year == movie_year).all()
        year_list = []
        for id in movie_filter_info:
            filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.db_id.contains(id.parent_id)).all()
            year_list.append(filter_info)
        return render_template('movie_year.html', movie_year = year_list)

@app.route('/skitunes/filtermovie')
@login_required
def filter_movie():
    name = request.args.get("movie_name")
    movie_info = db.session.query(Movie).filter(Movie.movie_name.contains(name)).all()
    movie_co = db.session.query(Movie).filter(Movie.movie_name.contains(name)).first()
    track_list = []
    for id in movie_info:
        filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.db_id.contains(id.parent_id)).all()
        track_list.append(filter_info)
    return render_template('movie_co.html', movie_co = track_list)

@app.route('/skitunes/filterskier')
@login_required
def filter():
    skier_name = request.args.get('skier_name')
    filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.skier_name.contains(skier_name)).all()
    return render_template('skibase.html', tracks = filter_info)

@app.route('/skitunes/filtersong')
@login_required
def filter_song():
    song_name = request.args.get("song_name")
    filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.song_name.contains(song_name)).all()
    return render_template('skibase.html', tracks = filter_info)

@app.route('/skitunes/filterartist')
@login_required
def filter_artist():
    song_artist = request.args.get("song_artist")
    filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.song_artist.contains(song_artist)).all()
    return render_template('skibase.html', tracks = filter_info)

@app.route('/skitunes/filteralbum')
@login_required
def filter_album():
    song_album = request.args.get("song_album")
    filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.song_album.contains(song_album)).all()
    return render_template('skibase.html', tracks = filter_info)

@app.route('/skitunes/filtermovieco')
@login_required
def filter_movieco():
    name = request.args.get("movie_co")
    movie_co = db.session.query(Movie).filter(Movie.movie_co.contains(name)).all()
    prod_list = []
    for id in movie_co:
        filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.db_id.contains(id.parent_id)).all()
        prod_list.append(filter_info)
    return render_template('movie_co.html', movie_co = prod_list)

@app.route('/skitunes/filterlocation')
@login_required
def filter_location():
    location = request.args.get("location")
    filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.location.contains(location)).all()
    return render_template('skibase.html', tracks = filter_info)

@app.route('/skitunes/filtertype')
@login_required
def filter_type():
    ski_type = request.args.get("ski_type")
    filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.ski_type.contains(ski_type)).all()
    return render_template('skibase.html', tracks = filter_info)

@app.route('/skitunes/likewhat')
@login_required
def like_what():
    return render_template('likewhat.html')

@app.route('/skitunes/create_playlist', methods=['GET', 'POST'])
@login_required
def create_playlist_url():
    spotify_id = session['spotify_user_id']
    playlist_name = request.form['playlist_name']
    track_list = []
    for spotify_link in request.form.getlist('selected_track'):
        spotify_track_id = spotify_link.replace("https://open.spotify.com/track/","")
        playlist_value = "spotify:track:" + spotify_track_id
        if playlist_value in track_list:
            pass
        else:
            track_list.append(playlist_value)
    response = create_playlist(spotify_id, playlist_name)
    create_code = response.status_code
    response = response.json()
    try:
        new_playlist_uri = response['uri']
    except KeyError:
        flash('Issue creating playlist. Try logging back in to Spotify')
        return redirect(url_for('skitunes'))
    new_playlist_uri = new_playlist_uri.replace('spotify:playlist:','')
    if len(track_list) > 100:
        step = 100
        for i in range(0,len(track_list),step):
            x = i
            short_list = track_list[x:x+step]
            add_track_response = add_tracks(new_playlist_uri, short_list)
    else:
        add_track_response = add_tracks(new_playlist_uri, track_list)
    add_track_response_code = add_track_response.status_code
    if create_code == 201 and add_track_response_code == 201:
        flash('Playlist ' + playlist_name + ' was created and ' + str(len(track_list)) + ' tracks were added.')
        return redirect(url_for('home'))
    elif create_code != 201:
        flash('Error creating new playlist')
        return redirect(url_for('home'))
    elif add_track_response_code != 201:
        flash('Error adding tracks, the playlist was created but is most likely empty')
        return redirect(url_for('home'))

@app.route('/new_entry', methods=['GET', 'POST'])
@login_required
def new_entry():
    if request.method == 'POST':
        if not request.form['song_name']:
            flash('Please enter all the fields', 'error')
        else:
            try:
                movie_song_info = ski_movie_song_info(song_name = request.form['song_name'], song_artist = request.form['song_artist'], song_album = request.form['song_album'], song_num=request.form['song_num'], spotify_id=request.form['spotify_link'], skier_name = request.form['skier_name'], movie_name = request.form['movie_name'], movie_year=request.form['movie_year'], movie_co=request.form['movie_co'], ski_type = request.form['ski_type'], location=request.form['location'], video_link = request.form['video_link'])           
                db.session.add(movie_song_info)
                db.session.commit()

                flash('Record was successfully added')
                return redirect(url_for('skitunes'))
            except:
                flash('There was an error adding the record. Make sure it does not already exist')
                return redirect(url_for('skitunes'))
    return render_template('new_entry.html')

@app.route('/edit_entry/<entry>', methods=['GET', 'POST'])
@login_required
def edit_entry(entry):
    song_data = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.db_id == entry)
    if request.method == 'POST':
        if not request.form['song_name']:
            flash('Please enter all the fields', 'error')
        else:
            movie_song_info = ski_movie_song_info(song_name = request.form['song_name'], song_artist = request.form['song_artist'], song_album = request.form['song_album'], song_num=request.form['song_num'], spotify_id=request.form['spotify_link'], skier_name = request.form['skier_name'], movie_name = request.form['movie_name'], movie_year=request.form['movie_year'], movie_co=request.form['movie_co'], ski_type = request.form['ski_type'], location=request.form['location'], video_link = request.form['video_link'])           
            db.session.add(movie_song_info)
            db.session.commit()

            flash('Record was successfully added')
            return redirect(url_for('skitunes'))
    return render_template('edit_entry.html', song_data=song_data)

@app.route('/delete_entry/<entry>', methods=['GET', 'POST'])
@login_required
def delete_entry(entry):
    song_data = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.db_id == entry)
    if request.method == 'POST':
        db.session.query(ski_movie_song_info).filter(ski_movie_song_info.db_id == entry).delete()
        db.session.commit()
        flash('Record was deleted')
        name = current_user.name
        profile_pic = current_user.profile_pic
        return render_template('skitunes.html', name=name, profile_pic=profile_pic)
    return render_template('delete_entry.html', song_data=song_data)

@app.route('/bulkImport', methods=['GET', 'POST'])
@login_required
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
        movie = Movie(movie_name=movie_name,movie_year=movie_year,movie_co=movie_co,movie_img_url='None')
        movie_song_info = ski_movie_song_info(song_name = song_name, song_artist = song_artist, song_album = song_album, song_num=song_num, spotify_id=spotify_link, skier_name = skier_name, ski_type = ski_type, location=location, video_link = video_link)
        movie_song_info.movie_details.append(movie)
        db.session.add(movie_song_info)
        db.session.commit()
    return jsonify(json_playlist)
