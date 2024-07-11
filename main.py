#!/usr/bin/env python3.11

from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from show_classes import Show
import json
from fuzzywuzzy import fuzz
import spotipy
from spotipy import SpotifyClientCredentials
from typing import List
import pandas as pd
from spotipy.oauth2 import SpotifyOAuth
import time
from numpy import round as np_round

"""Get the keys from the keys.json file"""
def get_keys():
    with open('keys.json') as f:
        keys = json.load(f)
    return keys

"""Run the Soup to get the HTML page"""
def get_soup(url):
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)  
    try:
        # Fetch the webpage
        url = url
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        return soup
    finally:
        # Close the browser
        driver.quit()

"""Init the client"""
def init_client():
    keys = get_keys()
    client_id = keys['client_id']
    client_secret = keys['client_secret']
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri='http://localhost:8080/callback', scope='user-read-currently-playing playlist-modify-private streaming user-modify-playback-state'))
    return sp

def parse_song_info(results):
    search_bank = []
    for i in (results['tracks']['items']):
        name = i['name']
        artists = ', '.join([i['name'] for i in i['artists']])
        url = i['external_urls']['spotify']
        id = i['id']
        search_bank.append({'name': name, 'artists': artists, 'url': url, 'id': id})
    return search_bank

search_limit = 10

"""Get matches against the search engine"""
def get_matches(client, show_track_list):
    matches = []
    for track in show_track_list:
        sample_song = f'{track.title} - {track.artist}'
        results = client.search(q=sample_song, limit=search_limit)
        check = parse_song_info(results)
        
        ratio_bank = []
        # go through each search result and calculate the score, use fuzz to get the similarity score, temporarily use token_sort_ratio
        for candidate in check:
            check_str = f'{candidate["name"]}, {candidate["artists"]}'
            ratio1 = fuzz.token_sort_ratio(candidate['name'], track.title)
            ratio2 = fuzz.token_sort_ratio(candidate['artists'], track.artist)
            ratio_bank.append((ratio1+ratio2)/2)
        
        # np argmax of the indx
        index = ratio_bank.index(max(ratio_bank))
        matches.append(check[index])
    return matches

"""Make the playlist"""
def make_playlist(client, results, show):
    # Information
    user_id = client.me()['id']
    host = show.show_metadata['host']
    date = show.show_metadata['date_aired']
    title = show.title
    playlist_title = f'{host} - {title}'
    playlist_desc = f'{show.details} - Aired: {date}'
    
    # Playlist creation
    playlist = client.user_playlist_create(user=user_id, name=playlist_title, description=playlist_desc, collaborative=False, public=False)
    playlist_id = playlist['id']

    # Add the songs
    for song in results:
        client.playlist_add_items(playlist_id, [song['id']])
    print(f'Playlist {playlist_title} has been created')

def main(page):
    start_time = time.time()
    # Get the HTML and parse for show class
    soup = get_soup(page)
    show = Show(soup)
    show.get_track_list()
    show.access_metadata()
    print(f'{show.__repr__} ---> Done Parsing')

    # Initialize the client
    sp_client = init_client()

    # Get the matches
    matches = get_matches(sp_client, show.track_list)
    print(f'{len(matches)} matches ---> Done Matching')

    # Create the playlist
    make_playlist(sp_client, matches, show)
    print('Done')
    print("--- %s seconds ---" % np_round(time.time() - start_time, 2))

if __name__ == '__main__':
    url = 'https://www.bbc.co.uk/sounds/play/m001zzyx' # Target URL for the BBC sounds page
    main(url)

