import base64
import requests
import time

SPOTIFY_AUTH_URL = "https://accounts.spotify.com"
SPOTIFY_API_URL = "https://api.spotify.com/v1"
SPOTIFY_SCOPES = "playlist-modify-private user-read-private"
SPOTIFY_REDIRECT_URI = "http://localhost"

class Spotify:

    client_id = ""
    client_secret = ""
    client_base64 = ""
    access_token = ""
    refresh_token = ""
    token_type = ""
    expiration_date = 0

    def set_credentials(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.client_base64 = base64.b64encode(bytes(client_id + ":" + client_secret, "ascii")).decode("ascii")

    def get_authorization_url(self):
        return SPOTIFY_AUTH_URL + "/authorize?client_id=" + self.client_id + "&response_type=code&redirect_uri=" + SPOTIFY_REDIRECT_URI + "&scope=" + SPOTIFY_SCOPES.replace(" ", "%20")

    def authorize(self, code):
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": SPOTIFY_REDIRECT_URI
        }
        headers = { "Authorization": "Basic " + self.client_base64 }
        response = requests.post(SPOTIFY_AUTH_URL + "/api/token", data=payload, headers=headers)
        json_response = response.json()
        self.access_token = json_response["access_token"]
        self.refresh_token = json_response["refresh_token"]
        self.token_type = json_response["token_type"]
        self.expiration_date = time.time() + json_response["expires_in"]
        return self.refresh_token

    def refresh(self):
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }
        headers = { "Authorization": "Basic " + self.client_base64 }
        response = requests.post(SPOTIFY_AUTH_URL + "/api/token", data=payload, headers=headers)
        json_response = response.json()
        self.access_token = json_response["access_token"]
        self.token_type = json_response["token_type"]
        self.expiration_date = time.time() + json_response["expires_in"]

    def search(self, query):
        if time.time() > self.expiration_date:
            self.refresh()
        payload = {
            "q": query,
            "type": "track",
            "limit": 1
        }
        headers = { "Authorization": "Bearer " + self.access_token }
        response = requests.get(SPOTIFY_API_URL + "/search", params=payload, headers=headers)
        if not response.ok or response.json()["tracks"]["total"] == 0:
            return None
        return response.json()["tracks"]["items"][0]

    def add_to_playlist(self, playlist_id, track):
        if time.time() > self.expiration_date:
            self.refresh()
        payload = '{ "uris": [ "' + track["uri"] + '" ] }'
        headers = { "Authorization": "Bearer " + self.access_token }
        response = requests.post(SPOTIFY_API_URL + "/playlists/" + playlist_id + "/tracks", data=payload, headers=headers)
        return response.ok
