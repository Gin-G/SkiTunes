import json

from matplotlib.font_manager import json_dump
# Let's finese some data

master_list = []
with open('playlist.json') as my_json:
    json_info = json.load(my_json)
    with open('Steve_data.csv') as file:
        for line in file:
            line = line.replace('\n','').split(',')
            movie_name = line[0]
            movie_year = line[1]
            movie_co = line[2]
            song_num = line[3]
            song_artist = line[4]
            song_name = line[5]
            song_album = line[6]
            spotify_link = line[7]
            ski_type = line[8]
            skier_name = line[9]
            location = line[10]
            for key in json_info:
                artist_name = key['track']['artists'][0]['name']
                track_name = key['track']['name']
                spotify_id = key['track']['id']
                #print(movie_name, movie_year, movie_co, song_num, song_artist, song_name, song_album, spotify_link, ski_type, skier_name, location)
                if artist_name == song_artist:
                    if track_name == song_name:
                        spotify_link = 'https://open.spotify.com/track/' + spotify_id
                else:
                    pass
            entry = {"Movie Name" : movie_name,"Movie Year" :  movie_year,"Production Co." : movie_co, "Song Number" : song_num, "Artist" : song_artist, "Song Name"  : song_name, "Song Album" : song_album, "Spotify Link": spotify_link, "Skiing type":ski_type, "Skier Name(s)":skier_name, "Location":location}
            master_list.append(entry)

with open('clean_data.json', 'w') as outfile:
    json.dump(master_list, outfile)
'''

json_playlist = open('clean_data.json')
json_playlist = json.load(json_playlist)
for track in json_playlist:
    print(track['Movie Name'])
'''