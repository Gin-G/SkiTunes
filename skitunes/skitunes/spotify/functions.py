from email.mime import base
from flask import redirect, session
from matplotlib.pyplot import get
import requests
from requests.auth import HTTPBasicAuth
import json
import os
import base64
from skitunes.variables.variables import *

def spotify_auth():
    auth_response = requests.post(AUTH_URL, {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })

    auth_response_data = auth_response.json()

    # save the access token
    access_token = auth_response_data['access_token']

    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token)
    }

    return headers

def authorize(auth_token):
    payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": spotify_redirect_uri_url
    }

    auth_response = requests.post(AUTH_URL, auth=HTTPBasicAuth(client_id, client_secret), data=payload)
    auth_response_data = auth_response.json()

    # save the access token
    
    return auth_response_data

def spotify_search_song(track):
    headers = spotify_auth()
    params = {'q' : track, 'type' : 'track,artist', 'limit' : 1}
    # actual GET request with proper header
    track_info = requests.get(base_spotify_url + 'search?', headers=headers, params=params)
    track_info = track_info.json()
    try:
        url = track_info['tracks']['items'][0]['external_urls']['spotify']
        album = track_info['tracks']['items'][0]['album']['name']
        name = track_info['tracks']['items'][0]['name']
        artist = track_info['tracks']['items'][0]['artists'][0]['name']
        genres = track_info['artists']['items'][0]['genres']
        return url, album, name, artist, genres
    except IndexError:
        return "Not Found", "Not Found", "Not Found", "Not Found", "Not Found"
    except TypeError:
        return "Not Found", "Not Found", "Not Found", "Not Found", "Not Found"

def get_track_info():
    headers = spotify_auth()
    # Track ID from the URI
    track_id = '6y0igZArWVi6Iz0rj35c1Y'

    # actual GET request with proper header
    track_info = requests.get(base_spotify_url + 'audio-features/' + track_id, headers=headers)
    return track_info.json()


def get_artist_albums():
    headers = spotify_auth()
    artist_id = '36QJpDe2go2KgaRleHCDTp'

    # pull all artists albums

    artist_album = requests.get(base_spotify_url + 'artists/' + artist_id + '/albums', 
                    headers=headers, 
                    params={'include_groups': 'album', 'limit': 50})

def get_playlist_info():
    headers = spotify_auth()
    #playlist_id = '4SJybMaIGipeMLrtiNamXD'
    playlist_id = '18go8B8q3kzmw6QhE9BBlk'
    tracks = requests.get(base_spotify_url + 'playlists/' + playlist_id + "/tracks?fields=items(track.id),total", headers=headers)
    tracks = tracks.json()
    total = int(tracks['total'])
    offset = 0
    playlist_info = []
    while offset < total:
        playlist = requests.get(base_spotify_url + 'playlists/' + playlist_id + "/tracks?fields=items(track.name,track.id,track.artists.name)&offset=" + str(offset), headers=headers)
        playlist = playlist.json()
        playlist = playlist['items']
        for track in playlist:
            if track['track']['name'] in playlist_info:
                pass
            else:
                playlist_info.append(track)
        offset+=100
    playlist_info = json.dumps(playlist_info, indent=2)
    print(playlist_info)

def create_playlist(username, playlist_name):
    headers = {"Authorization": "Bearer {}".format(session['spotify_access_token'])}
    url = 	'https://api.spotify.com/v1/users/' + username + '/playlists'
    description = "Created by skimoviesongs.com based on " + username + "'s input" 
    json_body = {
        "name": str(playlist_name),
        "description": str(description)
    }
    created = requests.post(url, headers=headers, data=json.dumps(json_body))
    return created

def add_tracks(playlist_id, track_list):
    headers = {"Authorization": "Bearer {}".format(session['spotify_access_token'])}
    url = 	'https://api.spotify.com/v1/playlists/' + playlist_id + '/tracks'
    json_body = {
        "uris": track_list,
        "position": 0
    }
    created = requests.post(url, headers=headers, data=json.dumps(json_body))
    return created

def get_user():
    headers = {"Authorization": "Bearer {}".format(session['spotify_access_token'])}
    response = requests.get(SPOTIFY_USER_URL, headers=headers)
    return response