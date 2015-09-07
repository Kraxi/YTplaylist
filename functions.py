import httplib2
import os
import sys
import datetime
import requests

import gdata.youtube
import gdata.youtube.service

from lxml import html
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow



def authentication():



    # The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
    # the OAuth 2.0 information for this application, including its client_id and
    # client_secret. You can acquire an OAuth 2.0 client ID and client secret from
    # the Google Developers Console at
    # https://console.developers.google.com/.
    # Please ensure that you have enabled the YouTube Data API for your project.
    # For more information about using OAuth2 to access the YouTube Data API, see:
    #   https://developers.google.com/youtube/v3/guides/authentication
    # For more information about the client_secrets.json file format, see:
    #   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
    CLIENT_SECRETS_FILE = "client_secrets.json"

    # This variable defines a message to display if the CLIENT_SECRETS_FILE is
    # missing.
    MISSING_CLIENT_SECRETS_MESSAGE = """
    WARNING: Please configure OAuth 2.0

    To make this sample run you will need to populate the client_secrets.json file
    found at:

       %s

    with information from the Developers Console
    https://console.developers.google.com/

    For more information about the client_secrets.json file format, please visit:
    https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
    """ % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                       CLIENT_SECRETS_FILE))

    # This OAuth 2.0 access scope allows for full read/write access to the
    # authenticated user's account.
    YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"

    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
      message=MISSING_CLIENT_SECRETS_MESSAGE,
      scope=YOUTUBE_READ_WRITE_SCOPE)

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
      flags = argparser.parse_args()
      credentials = run_flow(flow, storage, flags)

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
      http=credentials.authorize(httplib2.Http()))
    return youtube;

def create_playlist(yt_service, radio):

    now = datetime.datetime.now()
    t = ""
    d = ""
    if radio == "RMF":
        t = "RMF Playlist"+" "+str(now.year)+"-"+str(now.month)+"-"+str(now.day)
        d = "RMF FM playlist - TOP 40"
    elif radio == "Trojka":
        t = "Notowanie Trojki"+" "+str(now.year)+"-"+str(now.month)+"-"+str(now.day)
        d = "Trojka playlist - TOP 30"
    playlists_insert_response = yt_service.playlists().insert(
      part="snippet,status",
      body=dict(
        snippet=dict(
          title=t,
          description=d
        ),
        status=dict(
          privacyStatus="private"
        )
      )
    ).execute()

    print "New playlist id: %s" % playlists_insert_response["id"]
    return playlists_insert_response["id"];

def add_video_to_playlist(youtube,videoID,playlistID):
    add_video_request=youtube.playlistItems().insert(
    part="snippet",
    body={  'snippet': {
              'playlistId': playlistID, 
              'resourceId': {
                      'kind': 'youtube#video',
                  'videoId': videoID
                }
            #'position': 0
            }
     }
     ).execute()
    return;

def get_rmf_list():

    response = requests.get("http://www.rmf.fm/au/?a=poplista")
    tree = html.fromstring(response.text)

    artists = tree.xpath('//div[@class="poplista-artist-title"]/text()')
    artysci = tree.find_class('poplista-artist-title')#all divs with artist name
    kawalki = tree.find_class('poplista-title')#All divs with song title
    przeboje = []
    for x in range(len(artysci)):
        a = artysci[x][0].text
        t = kawalki[x].text
        przeboje.append(a + ',' + t)
    #print przeboje
    return przeboje;   

def get_trojka_list():
    
    response = requests.get("http://lp3.polskieradio.pl/notowania/")
    tree = html.fromstring(response.text)

    #artists = tree.xpath('//div[@class="bArtist"]/text()')
    artysci = tree.find_class('bArtist')#all divs with artist name
    kawalki = tree.find_class('bTitle')#All divs with song title
    przeboje = []
    for x in range(50):
        a = artysci[x][0].text
        t = kawalki[x][0].text        
        przeboje.append(a + ',' + t)

    #print przeboje
    return przeboje;   

def search(youtube, keyword):
    # Call the search.list method to retrieve results matching the specified
    # query term.
    search_response = youtube.search().list(q=keyword,part="id,snippet",maxResults=10,type="video").execute()
    videos = []
    # Add each result to the appropriate list, and then display the lists of
    # matching videos, channels, and playlists.
    for search_result in search_response.get("items", []):
        videos.append(search_result["id"]["videoId"])
    return videos[0]

def feed_playlist(youtube, radio):
    przeboje = []
    if radio == "RMF":
        przeboje = get_rmf_list()
    elif radio == "Trojka":
        przeboje = get_trojka_list()
    playlist_id = create_playlist(youtube, radio)
    for x in range(len(przeboje)):
        keyword = przeboje[x].replace(","," ")
        add_video_to_playlist(youtube, search(youtube, keyword), playlist_id)
        print "Added: " + keyword
    return;
    

