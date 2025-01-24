from textwrap import indent

from flask import request, flash, redirect, url_for, jsonify, send_file, session
from flask_login import current_user, LoginManager, login_required, login_user, logout_user
import logging
from skitunes import app, db, mail
from skitunes.spotify.models import ski_movie_song_info, Movie
from skitunes.spotify.functions import create_playlist, add_tracks
from skitunes.main.forms import MovieSearchForm
from skitunes.account.models import User
from flask.templating import render_template
from flask_mail import Message
import smtplib
import requests
import os
import json

#logger = logging.getLogger(__name__)
#log = logging.getLogger('werkzeug')
#log.setLevel(logging.ERROR)

@app.before_request
def create_tables():
    db.create_all()

@app.route('/')
def home():
    form = MovieSearchForm()
    if current_user.is_authenticated:
        name = current_user.name
        profile_pic = current_user.profile_pic
        return render_template('skitunes.html', name=name, profile_pic=profile_pic, form=form)
    else:
        return render_template('skitunes.html', form=form)

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
def create_playlist_js():
    return render_template('create_playlist.html')

@app.route('/skitunes')
def skitunes():
    form = MovieSearchForm()
    return render_template('skitunes.html', form = form)

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
        filter_info = db.session.query(ski_movie_song_info).filter(
            ski_movie_song_info.db_id == id.parent_id 
        ).all()
        prod_list.append(filter_info)
    return render_template('movie_co.html', movie_co=prod_list)

@app.route('/skitunes/skibase/movie/year/<year>')
@login_required
def year(year):
    movie_year = db.session.query(Movie).filter(Movie.movie_year == year).all()
    year_list = []
    for id in movie_year:
        filter_info = db.session.query(ski_movie_song_info).filter(
            ski_movie_song_info.db_id == id.parent_id
        ).all()
        year_list.append(filter_info)
    return render_template('movie_year.html', movie_year=year_list)

@app.route('/skitunes/skibase/movie/<name>')
@login_required
def ski_movie(name):
    # Use exact matching instead of contains()
    movie_info = db.session.query(Movie).filter(Movie.movie_name == name).all()
    movie_co = db.session.query(Movie).filter(Movie.movie_name == name).first()
    
    track_list = []
    for id in movie_info:
        # Also check if this filter should use exact matching
        filter_info = db.session.query(ski_movie_song_info).filter(
            ski_movie_song_info.db_id == id.parent_id  # Changed to exact matching
        ).all()
        track_list.append(filter_info)
    
    return render_template(
        'movie_info.html',
        movie_info=track_list,
        movie_name=str(name),
        movie_co=movie_co
    )

@app.route('/skitunes/skibase_lite')
@login_required
def skibase_lite():
    tracks = ski_movie_song_info.query.all()
    return render_template('skibase_lite.html', tracks = tracks)

@app.route('/skitunes/findmovie')
def findmovie():
    user_agent = request.headers.get('User-Agent')
    user_agent = user_agent.lower()
    log_info = "USER-AGENT : " + user_agent
    # logger.info('%s', log_info)
    if "iphone" in user_agent:
        try:
            song_name = request.args.get('song_name')
            song_artist = request.args.get('song_artist')
            movie_year = request.args.get('movie_year')
            movie_year2 = request.args.get('movie_year2')
            if len(song_artist) != 0:
                if len(song_name) != 0:
                    log_info = "SEARCH - SONG_NAME : " + song_name + " SONG_ARTIST : " + song_artist
                    # logger.info('%s', log_info)
                    filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.song_name.contains(song_name),ski_movie_song_info.song_artist.contains(song_artist)).all()
                    return render_template('skibase_lite.html', tracks = filter_info)
                else:
                    log_info = "SEARCH - SONG_ARTIST : " + song_artist
                    # logger.info('%s', log_info)
                    filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.song_artist.contains(song_artist)).all()
                return render_template('skibase_lite.html', tracks = filter_info)
            elif len(song_name) != 0:
                log_info = "SEARCH - SONG_NAME : " + song_name
                # logger.info('%s', log_info)
                filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.song_name.contains(song_name)).all()
                return render_template('skibase_lite.html', tracks = filter_info)
            elif len(movie_year) != 0:
                if len(movie_year2) != 0:
                    log_info = "SEARCH - RANGE MOVIE_YEAR : " + movie_year + " to " + movie_year2
                    # logger.info('%s', log_info)
                    year_list = []
                    if int(movie_year) > int(movie_year2):
                        years = range(int(movie_year), int(movie_year2)+1, 1)
                        for year in years:
                            movie_filter_info = db.session.query(Movie).filter(Movie.movie_year == year).all()
                            for id in movie_filter_info:
                                filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.db_id.contains(id.parent_id)).all()
                                year_list.append(filter_info)
                        return render_template('movie_year_lite.html', movie_year = year_list)
                    elif int(movie_year) < int(movie_year2):
                        years = range(int(movie_year2), int(movie_year)+1, 1)
                        for year in years:
                            movie_filter_info = db.session.query(Movie).filter(Movie.movie_year == year).all()
                            for id in movie_filter_info:
                                filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.db_id.contains(id.parent_id)).all()
                                year_list.append(filter_info)
                        return render_template('movie_year_lite.html', movie_year = year_list)
                else:
                    log_info = "SEARCH - MOVIE_YEAR : " + movie_year
                    # logger.info('%s', log_info)
                    movie_filter_info = db.session.query(Movie).filter(Movie.movie_year == movie_year).all()
                    year_list = []
                    for id in movie_filter_info:
                        filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.db_id.contains(id.parent_id)).all()
                        year_list.append(filter_info)
                    return render_template('movie_year_lite.html', movie_year = year_list)
            else:
                log_info = "SEARCH - ALL"
                # logger.info('%s', log_info)
                tracks = ski_movie_song_info.query.all()
                return render_template('skibase_lite.html', tracks = tracks)
        except TypeError:
            log_info = "Type Error - returned all tracks"
            # logger.info('%s', log_info)
            tracks = ski_movie_song_info.query.all()
            return render_template('skibase_lite.html', tracks = tracks)
    elif "android" in user_agent:
        try:
            song_name = request.args.get('song_name')
            song_artist = request.args.get('song_artist')
            movie_year = request.args.get('movie_year')
            movie_year2 = request.args.get('movie_year2')
            if len(song_artist) != 0:
                if len(song_name) != 0:
                    log_info = "SEARCH - SONG_NAME : " + song_name + " SONG_ARTIST : " + song_artist
                    # logger.info('%s', log_info)
                    filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.song_name.contains(song_name),ski_movie_song_info.song_artist.contains(song_artist)).all()
                    return render_template('skibase_lite.html', tracks = filter_info)
                else:
                    log_info = "SEARCH - SONG_ARTIST : " + song_artist
                    # logger.info('%s', log_info)
                    filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.song_artist.contains(song_artist)).all()
                return render_template('skibase_lite.html', tracks = filter_info)
            elif len(song_name) != 0:
                log_info = "SEARCH - SONG_NAME : " + song_name
                # logger.info('%s', log_info)
                filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.song_name.contains(song_name)).all()
                return render_template('skibase_lite.html', tracks = filter_info)
            elif len(movie_year) != 0:
                if len(movie_year2) != 0:
                    log_info = "SEARCH - RANGE MOVIE_YEAR : " + movie_year + " to " + movie_year2
                    # logger.info('%s', log_info)
                    year_list = []
                    if int(movie_year) > int(movie_year2):
                        years = range(int(movie_year), int(movie_year2)+1, 1)
                        for year in years:
                            movie_filter_info = db.session.query(Movie).filter(Movie.movie_year == year).all()
                            for id in movie_filter_info:
                                filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.db_id.contains(id.parent_id)).all()
                                year_list.append(filter_info)
                        return render_template('movie_year_lite.html', movie_year = year_list)
                    elif int(movie_year) < int(movie_year2):
                        years = range(int(movie_year2), int(movie_year)+1, 1)
                        for year in years:
                            movie_filter_info = db.session.query(Movie).filter(Movie.movie_year == year).all()
                            for id in movie_filter_info:
                                filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.db_id.contains(id.parent_id)).all()
                                year_list.append(filter_info)
                        return render_template('movie_year_lite.html', movie_year = year_list)
                else:
                    log_info = "SEARCH - MOVIE_YEAR : " + movie_year
                    # logger.info('%s', log_info)
                    movie_filter_info = db.session.query(Movie).filter(Movie.movie_year == movie_year).all()
                    year_list = []
                    for id in movie_filter_info:
                        filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.db_id.contains(id.parent_id)).all()
                        year_list.append(filter_info)
                    return render_template('movie_year_lite.html', movie_year = year_list)
            else:
                log_info = "SEARCH - ALL"
                # logger.info('%s', log_info)
                tracks = ski_movie_song_info.query.all()
                return render_template('skibase_lite.html', tracks = tracks)
        except TypeError:
            log_info = "Type Error - returned all tracks"
            # logger.info('%s', log_info)
            tracks = ski_movie_song_info.query.all()
            return render_template('skibase_lite.html', tracks = tracks)
    else:
        try:
            song_name = request.args.get('song_name')
            song_artist = request.args.get('song_artist')
            movie_year = request.args.get('movie_year')
            movie_year2 = request.args.get('movie_year2')
            if len(song_artist) != 0:
                if len(song_name) != 0:
                    log_info = "SEARCH - SONG_NAME : " + song_name + " SONG_ARTIST : " + song_artist
                    # logger.info('%s', log_info)
                    filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.song_name.contains(song_name),ski_movie_song_info.song_artist.contains(song_artist)).all()
                    return render_template('skibase.html', tracks = filter_info)
                else:
                    log_info = "SEARCH - SONG_ARTIST : " + song_artist
                    # logger.info('%s', log_info)
                    filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.song_artist.contains(song_artist)).all()
                return render_template('skibase.html', tracks = filter_info)
            elif len(song_name) != 0:
                log_info = "SEARCH - SONG_NAME : " + song_name
                # logger.info('%s', log_info)
                filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.song_name.contains(song_name)).all()
                return render_template('skibase.html', tracks = filter_info)
            elif len(movie_year) != 0:
                if len(movie_year2) != 0:
                    log_info = "SEARCH - RANGE MOVIE_YEAR : " + movie_year + " to " + movie_year2
                    # logger.info('%s', log_info)
                    year_list = []
                    if int(movie_year) > int(movie_year2):
                        years = range(int(movie_year), int(movie_year2)+1, 1)
                        for year in years:
                            movie_filter_info = db.session.query(Movie).filter(Movie.movie_year == year).all()
                            for id in movie_filter_info:
                                filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.db_id.contains(id.parent_id)).all()
                                year_list.append(filter_info)
                        return render_template('movie_year_lite.html', movie_year = year_list)
                    elif int(movie_year) < int(movie_year2):
                        years = range(int(movie_year2), int(movie_year)+1, 1)
                        for year in years:
                            movie_filter_info = db.session.query(Movie).filter(Movie.movie_year == year).all()
                            for id in movie_filter_info:
                                filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.db_id.contains(id.parent_id)).all()
                                year_list.append(filter_info)
                        return render_template('movie_year_lite.html', movie_year = year_list)
                else:
                    log_info = "SEARCH - MOVIE_YEAR : " + movie_year
                    # logger.info('%s', log_info)
                    movie_filter_info = db.session.query(Movie).filter(Movie.movie_year == movie_year).all()
                    year_list = []
                    for id in movie_filter_info:
                        filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.db_id.contains(id.parent_id)).all()
                        year_list.append(filter_info)
                    return render_template('movie_year.html', movie_year = year_list)
            else:
                log_info = "SEARCH - ALL"
                # logger.info('%s', log_info)
                tracks = ski_movie_song_info.query.all()
                return render_template('skibase.html', tracks = tracks)
        except TypeError as e:
            log_info = "Type Error - returned all tracks" + str(e)
            # logger.info('%s', log_info)
            tracks = ski_movie_song_info.query.all()
            return render_template('skibase.html', tracks = tracks)

@app.route('/skitunes/filtermovie')
@login_required
def filter_movie():
    name = request.args.get("movie_name")
    
    # Query tracks associated with movies containing the search string
    tracks = (
        db.session.query(ski_movie_song_info)
        .join(ski_movie_song_info.movie_details)
        .filter(Movie.movie_name.contains(name))
        .all()
    )
    return render_template('skibase.html', tracks = tracks)

@app.route('/skitunes/filtermovielite')
@login_required
def filter_movie_lite():
    name = request.args.get("movie_name")
    
    # Query tracks associated with movies containing the search string
    tracks = (
        db.session.query(ski_movie_song_info)
        .join(ski_movie_song_info.movie_details)
        .filter(Movie.movie_name.contains(name))
        .all()
    )
    
    return render_template('skibase_lite.html', tracks=tracks)

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


@app.route('/skitunes/filtersonglite')
@login_required
def filter_song_lite():
    song_name = request.args.get("song_name")
    filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.song_name.contains(song_name)).all()
    return render_template('skibase_lite.html', tracks = filter_info)

@app.route('/skitunes/filterartistlite')
@login_required
def filter_artist_lite():
    song_artist = request.args.get("song_artist")
    filter_info = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.song_artist.contains(song_artist)).all()
    return render_template('skibase_lite.html', tracks = filter_info)

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
    
    # Query tracks associated with movies from the specified production company
    tracks = (
        db.session.query(ski_movie_song_info)
        .join(ski_movie_song_info.movie_details)
        .filter(Movie.movie_co.contains(name))
        .all()
    )
    
    return render_template('skibase.html', tracks=tracks)

@app.route('/skitunes/filtermoviecolite')
@login_required
def filter_movieco_lite():
    name = request.args.get("movie_co")
    
    # Query tracks associated with movies from the specified production company
    tracks = (
        db.session.query(ski_movie_song_info)
        .join(ski_movie_song_info.movie_details)
        .filter(Movie.movie_co.contains(name))
        .all()
    )
    
    return render_template('skibase_lite.html', tracks = tracks)

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
    print(request.form.getlist('selected_track'))
    for spotify_link in request.form.getlist('selected_track'):
        spotify_track_id = spotify_link.replace("https://open.spotify.com/track/","")
        playlist_value = "spotify:track:" + spotify_track_id
        if playlist_value in track_list:
            pass
        else:
            track_list.append(playlist_value)
    try:
        response = create_playlist(spotify_id, playlist_name)
    except AttributeError:
        flash('Issue creating playlist. Try logging back in to Spotify')
        return redirect(url_for('home'))
    create_code = response.status_code
    response = response.json()
    try:
        new_playlist_uri = response['uri']
    except KeyError:
        flash('Issue creating playlist. Try logging back in to Spotify')
        return redirect(url_for('home'))
    new_playlist_uri = new_playlist_uri.replace('spotify:playlist:','')
    print(track_list)
    print(len(track_list))
    if len(track_list) > 100:
        step = 100
        for i in range(0,len(track_list),step):
            x = i
            short_list = track_list[x:x+step]
            add_track_response = add_tracks(new_playlist_uri, short_list)
            print(add_track_response.json())
    else:
        add_track_response = add_tracks(new_playlist_uri, track_list)
        print(add_track_response.json())
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

@app.route('/correct_entry/<entry>', methods=['GET', 'POST'])
def submit_correction(entry):
    song_data = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.db_id == entry)
    if request.method == 'POST':
        diff_list = []
        song_name = request.form['song_name']
        song_artist = request.form['song_artist']
        song_album = request.form['song_album']
        genres = request.form['genres']
        song_num=request.form['song_num']
        spotify_id=request.form['spotify_id']
        skier_name = request.form['skier_name']
        movie_name = request.form['movie_name']
        movie_year=request.form['movie_year']
        movie_co=request.form['movie_co']
        ski_type = request.form['ski_type']
        location=request.form['location']
        video_link = request.form['video_link']
        orig_song_name = request.form['orig_song_name']
        orig_song_artist = request.form['orig_song_artist']
        orig_song_album = request.form['orig_song_album']
        orig_genres = request.form['orig_genres']
        orig_song_num=request.form['orig_song_num']
        orig_spotify_id=request.form['orig_spotify_id']
        orig_skier_name = request.form['orig_skier_name']
        orig_movie_name = request.form['orig_movie_name']
        orig_movie_year=request.form['orig_movie_year']
        orig_movie_co=request.form['orig_movie_co']
        orig_ski_type = request.form['orig_ski_type']
        orig_location=request.form['orig_location']
        orig_video_link = request.form['orig_video_link']       
        if song_name != orig_song_name:
            song_name_update = "Original name : " + orig_song_name + " was suggested to be changed to : " + song_name 
            diff_list.append(str(song_name_update))      
        if song_artist != orig_song_artist:
            song_artist_update = "Original artist : " + orig_song_artist + " was suggested to be changed to : " + song_artist 
            diff_list.append(str(song_artist_update))      
        if song_album != orig_song_album:
            song_album_update = "Original album : " + orig_song_album + " was suggested to be changed to : " + song_album 
            diff_list.append(str(song_album_update))        
        if genres != orig_genres:
            genres_update = "Original genres : " + orig_genres + " was suggested to be changed to : " + genres
            diff_list.append(str(genres_update))     
        if song_num != orig_song_num:
            song_num_update = "Original song # : " + orig_song_num + " was suggested to be changed to : " + song_num 
            diff_list.append(str(song_num_update))      
        if spotify_id != orig_spotify_id:
            spotify_id_update = "Original Spotify link : " + orig_spotify_id + " was suggested to be changed to : " + spotify_id 
            diff_list.append(str(spotify_id_update))      
        if skier_name != orig_skier_name:
            skier_name_update = "Original Skier name : " + orig_skier_name + " was suggested to be changed to : " + skier_name 
            diff_list.append(str(skier_name_update))      
        if movie_name != orig_movie_name:
            movie_name_update = "Original Movie name : " + orig_movie_name + " was suggested to be changed to : " + movie_name 
            diff_list.append(str(movie_name_update))      
        if movie_year != orig_movie_year:
            movie_year_update = "Original Movie Year : " + orig_movie_year + " was suggested to be changed to : " + movie_year 
            diff_list.append(str(movie_year_update))      
        if movie_co != orig_movie_co:
            movie_co_update = "Original Production company : " + orig_movie_co + " was suggested to be changed to : " + movie_co 
            diff_list.append(str(movie_co_update))      
        if ski_type != orig_ski_type:
            ski_type_update = "Original segment type : " + orig_song_name + " was suggested to be changed to : " + ski_type 
            diff_list.append(str(ski_type_update))      
        if location != orig_location:
            location_update = "Original location : " + orig_song_name + " was suggested to be changed to : " + location 
            diff_list.append(str(location_update))      
        if video_link != orig_video_link:
            video_link_update = "Original video link : " + orig_song_name + " was suggested to be changed to : " + video_link 
            diff_list.append(str(video_link_update))
        msg = Message('SMS User Correction', sender = 'NickCo7@gmail.com', recipients = ['NickCo7@gmail.com'])
        msg.body = str(diff_list).replace("', '","\n").replace("['",'').replace("']",'')
        try:
            mail.send(msg)
            flash("Email sent with correction suggestions for approval")
            return render_template('skitunes.html')
        except smtplib.SMTPException:
            flash("Email send error")
            return render_template('skitunes.html')
    return render_template('correct_entry.html', song_data=song_data)

@app.route('/delete_entry/<entry>', methods=['GET', 'POST'])
@login_required
def delete_entry(entry):
    form = MovieSearchForm()
    song_data = db.session.query(ski_movie_song_info).filter(ski_movie_song_info.db_id == entry)
    if request.method == 'POST':
        db.session.query(ski_movie_song_info).filter(ski_movie_song_info.db_id == entry).delete()
        db.session.commit()
        flash('Record was deleted')
        return render_template('skitunes.html', form=form)
    return render_template('delete_entry.html', song_data=song_data)

@app.route('/bulkImport', methods=['GET', 'POST'])
@login_required
def bulk_import():
    json_playlist = open('clean_data.json')
    json_playlist = json.load(json_playlist)
    
    success_count = 0
    duplicate_count = 0
    total_entries = len(json_playlist)
    
    print(f"Total entries to process: {total_entries}")
    
    for track in json_playlist:
        # For debugging, create the query separately
        query = db.session.query(ski_movie_song_info)\
            .join(ski_movie_song_info.movie_details)\
            .filter(
                ski_movie_song_info.song_name == track["Song Name"],
                ski_movie_song_info.song_artist == track["Artist"],
                ski_movie_song_info.song_album == track["Song Album"],
                ski_movie_song_info.song_num == track["Song Number"],
                ski_movie_song_info.genres == str(track["Genres"]) if track["Genres"] != "[]" else "Unknown",
                ski_movie_song_info.spotify_id == track["Spotify Link"],
                ski_movie_song_info.skier_name == track["Skier Name(s)"],
                ski_movie_song_info.ski_type == track["Skiing type"],
                ski_movie_song_info.location == track["Location"],
                Movie.movie_name == track["Movie Name"],
                Movie.movie_year == track["Movie Year"],
                Movie.movie_co == track["Production Co."]
            )
        
        existing_entry = query.first()
        
        if not existing_entry:
            
            movie = Movie(
                movie_name=track["Movie Name"],
                movie_year=track["Movie Year"],
                movie_co=track["Production Co."],
                movie_img_url='None'
            )
            
            movie_song_info = ski_movie_song_info(
                song_name=track["Song Name"],
                song_artist=track["Artist"],
                song_album=track["Song Album"],
                song_num=track["Song Number"],
                genres=str(track["Genres"]) if track["Genres"] != "[]" else "Unknown",
                spotify_id=track["Spotify Link"],
                skier_name=track["Skier Name(s)"],
                ski_type=track["Skiing type"],
                location=track["Location"],
                video_link='Unknown'
            )
            
            movie_song_info.movie_details.append(movie)
            db.session.add(movie_song_info)
            success_count += 1
        else:
            duplicate_count += 1
    
    db.session.commit()
    
    print(f"\nFinal counts:")
    print(f"Total entries processed: {total_entries}")
    print(f"Successful additions: {success_count}")
    print(f"Duplicates skipped: {duplicate_count}")
    
    flash(f'Bulk Import completed: {success_count} entries added, {duplicate_count} duplicates skipped')
    return redirect(url_for('home'))

# In your routes.py or app.py
@app.route('/admin/users')
@login_required
def admin_users():
    # Check if current user is admin
    if current_user.email not in ['nickco7@gmail.com', 'sgmorgan16@gmail.com']:
        flash('Unauthorized access')
        return redirect(url_for('home'))
    
    # Get all users
    users = User.query.all()
    return render_template('admin_users.html', users=users)