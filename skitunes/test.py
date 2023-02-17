import json
from skitunes.spotify.functions import spotify_search_song
from matplotlib.font_manager import json_dump
import csv
# Let's finese some data

master_list = []
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
        search = song_name.strip() + " " + song_artist.strip()
        try:
            url,album,spt_name,spt_art, genres = spotify_search_song(search)
            if spt_name == "Not Found":
                entry = {"Movie Name" : movie_name,"Movie Year" :  movie_year,"Production Co." : movie_co, "Song Number" : song_num, "Artist" : song_artist, "Song Name"  : song_name, "Song Album" : song_album, "Genres" : genres, "Spotify Link": url, "Skiing type":ski_type, "Skier Name(s)":skier_name, "Location":location}
                master_list.append(entry)
            else:
                if spt_art.lower() in song_artist.lower():
                    if spt_name.lower() in song_name.lower():
                        entry = {"Movie Name" : movie_name,"Movie Year" :  movie_year,"Production Co." : movie_co, "Song Number" : song_num, "Artist" : spt_art, "Song Name"  : spt_name, "Song Album" : album, "Genres" : genres, "Spotify Link": url, "Skiing type":ski_type, "Skier Name(s)":skier_name, "Location":location}
                        master_list.append(entry)
                    elif song_name.lower() in spt_name.lower():
                        entry = {"Movie Name" : movie_name,"Movie Year" :  movie_year,"Production Co." : movie_co, "Song Number" : song_num, "Artist" : spt_art, "Song Name"  : spt_name, "Song Album" : album, "Genres" : genres, "Spotify Link": url, "Skiing type":ski_type, "Skier Name(s)":skier_name, "Location":location}
                        master_list.append(entry)
                    else:
                        url = album = spt_name = spt_art = "Not Found"
                        entry = {"Movie Name" : movie_name,"Movie Year" :  movie_year,"Production Co." : movie_co, "Song Number" : song_num, "Artist" : song_artist, "Song Name"  : song_name, "Song Album" : song_album, "Genres" : genres, "Spotify Link": url, "Skiing type":ski_type, "Skier Name(s)":skier_name, "Location":location}
                        master_list.append(entry)
                elif song_artist.lower() in spt_art.lower():
                    if spt_name.lower() in song_name.lower():
                        entry = {"Movie Name" : movie_name,"Movie Year" :  movie_year,"Production Co." : movie_co, "Song Number" : song_num, "Artist" : spt_art, "Song Name"  : spt_name, "Song Album" : album, "Genres" : genres, "Spotify Link": url, "Skiing type":ski_type, "Skier Name(s)":skier_name, "Location":location}
                        master_list.append(entry)
                    elif song_name.lower() in spt_name.lower():
                        entry = {"Movie Name" : movie_name,"Movie Year" :  movie_year,"Production Co." : movie_co, "Song Number" : song_num, "Artist" : spt_art, "Song Name"  : spt_name, "Song Album" : album, "Genres" : genres, "Spotify Link": url, "Skiing type":ski_type, "Skier Name(s)":skier_name, "Location":location}
                        master_list.append(entry)
                    else:
                        url = album = spt_name = spt_art = "Not Found"
                        entry = {"Movie Name" : movie_name,"Movie Year" :  movie_year,"Production Co." : movie_co, "Song Number" : song_num, "Artist" : song_artist, "Song Name"  : song_name, "Song Album" : song_album, "Genres" : genres, "Spotify Link": url, "Skiing type":ski_type, "Skier Name(s)":skier_name, "Location":location}
                        master_list.append(entry)
                else:
                    url = album = spt_name = spt_art = "Not Found"
                    entry = {"Movie Name" : movie_name,"Movie Year" :  movie_year,"Production Co." : movie_co, "Song Number" : song_num, "Artist" : song_artist, "Song Name"  : song_name, "Song Album" : song_album, "Genres" : genres, "Spotify Link": url, "Skiing type":ski_type, "Skier Name(s)":skier_name, "Location":location}
                    master_list.append(entry)
        except:
            url = album = spt_name = spt_art = "Not Found"
            entry = {"Movie Name" : movie_name,"Movie Year" :  movie_year,"Production Co." : movie_co, "Song Number" : song_num, "Artist" : song_artist, "Song Name"  : song_name, "Song Album" : song_album, "Genres" : genres, "Spotify Link": url, "Skiing type":ski_type, "Skier Name(s)":skier_name, "Location":location}
            master_list.append(entry)


with open('clean_data.json', 'w') as outfile:
    json.dump(master_list, outfile)



'''
json_playlist = open('clean_data.json')
json_playlist = json.load(json_playlist)
for track in json_playlist:
    print(track['Movie Name'])



file = open('songs.csv')
list = csv.reader(file)
with open('out.csv','w+') as out:
    writer = csv.writer(out)
    for item in list:
        track = item[0].strip()
        artist = item[1].strip()
        search = track + " " + artist
        try:
            url,album,spt_name,spt_art = spotify_search_song(search)
            if spt_name == "Not Found":
                writer.writerow([track,artist,url,album,spt_name,spt_art])
            else:
                if spt_art.lower() in artist.lower():
                    if spt_name.lower() in track.lower():
                        writer.writerow([track,artist,url,album,spt_name,spt_art])
                    elif track.lower() in spt_name.lower():
                        writer.writerow([track,artist,url,album,spt_name,spt_art])
                    else:
                        url = album = spt_name = spt_art = "Not Found"
                        writer.writerow([track,artist,url,album,spt_name,spt_art])
                elif artist.lower() in spt_art.lower():
                    if spt_name.lower() in track.lower():
                        writer.writerow([track,artist,url,album,spt_name,spt_art])
                    elif track.lower() in spt_name.lower():
                        writer.writerow([track,artist,url,album,spt_name,spt_art])
                    else:
                        url = album = spt_name = spt_art = "Not Found"
                        writer.writerow([track,artist,url,album,spt_name,spt_art])
                else:
                    url = album = spt_name = spt_art = "Not Found"
                    writer.writerow([track,artist,url,album,spt_name,spt_art])
        except:
            url = album = spt_name = spt_art = "Not Found"
            writer.writerow([track,artist,url,album,spt_name,spt_art])
'''

        