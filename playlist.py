
import json
import uuid
import functions
import flask
import httplib2
import requests

from flask import Flask
from apiclient import discovery
from oauth2client import client


app = Flask(__name__)


# CLIENT_SECRETS, name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret, which are found
# on the API Access tab on the Google APIs
# Console <http://code.google.com/apis/console>
#CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), '..', 'client_secrets.json')

#FLOW = flow_from_clientsecrets(
#   CLIENT_SECRETS,
#    scope='https://www.googleapis.com/auth/plus.me',
#    redirect_uri='http://localhost:8000/oauth2callback')


@app.route('/')
def index():
  #if 'credentials' not in flask.session:
    #return flask.redirect(flask.url_for('oauth2callback'))
  #credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
  #if credentials.access_token_expired:
    #return flask.redirect(flask.url_for('oauth2callback'))
  #else:
    #http_auth = credentials.authorize(httplib2.Http())
    #yt_service = discovery.build('youtube', 'v3', http_auth)
    #functions.feed_playlist(yt_service)
    response = requests.get("http://www.rmf.fm/au/?a=poplista")
    return response.text


@app.route('/oauth2callback')
def oauth2callback():
  flow = client.flow_from_clientsecrets('youtube/client_secret.json',scope='https://www.googleapis.com/auth/youtube',redirect_uri=flask.url_for('oauth2callback', _external=True))
  if 'code' not in flask.request.args:
    auth_uri = flow.step1_get_authorize_url()
    return flask.redirect(auth_uri)
  else:
    auth_code = flask.request.args.get('code')
    credentials = flow.step2_exchange(auth_code)
    flask.session['credentials'] = credentials.to_json()
    return flask.redirect(flask.url_for('index'))

app.secret_key = str(uuid.uuid4())
