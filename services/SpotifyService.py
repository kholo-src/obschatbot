from services.Service import Service
from utils.OAuth2 import OAuth2
import base64
import requests

KNOWN_COMMANDS = ["addsong", "dellast", "playlist"]
USER_KEY = "last_song_added"

MSG_NOT_FOUND = "Aucun morceau trouvé :("
MSG_NOT_ADDED = "Le morceau n'a pas pu être ajouté"
MSG_NO_SONG = "Vous n'avez pas ajouté de morceau"
MSG_DELETED = "Le morceau a été supprimé"
MSG_NOT_DELETED = "Le morceau n'a pas pu être supprimé"

AUTH_URL = "https://accounts.spotify.com"
API_URL = "https://api.spotify.com/v1"
SPOTIFY_SCOPES = "playlist-modify-public playlist-modify-private user-read-private"

class SpotifyService(OAuth2, Service):

    code_url = f"{AUTH_URL}/authorize"
    authorization_url = f"{AUTH_URL}/api/token"
    refresh_url = f"{AUTH_URL}/api/token"
    scope = SPOTIFY_SCOPES
    playlist = ""

    # OAuth -----

    def get_client_headers(self):
        return base64.b64encode(bytes(f"{self.client_id}:{self.client_secret}", "ascii")).decode("ascii")

    # Service -----

    def knows(self, command):
        return command in KNOWN_COMMANDS

    def eval(self, command, response, users):
        if command == "addsong":
            user = response["username"]
            query = response["message"].split(" ", 1)[1]
            return self.add_song(user, query, users)
        elif command == "dellast":
            return self.del_last(response["username"], users)
        elif command == "playlist":
            return self.get_playlist_url()

    def list_commands(self):
        return KNOWN_COMMANDS

    # Settings -----

    def set_playlist(self, playlist):
        self.playlist = playlist

    # Commands -----

    def add_song(self, user, query, users):
        if self.has_expired():
            self.refresh()
        track = self.search(query)
        if track is None:
            return f"🎵 {MSG_NOT_FOUND} @{user} 🎵"
        if self.add_to_playlist(track):
            artist = track["artists"][0]["name"]
            title = track["name"]
            if user not in users:
                users[user] = {}
            users[user][USER_KEY] = track["uri"]
            return f"🎵 Le morceau '{title}' de {artist} a été ajouté 🎵"
        else:
            return f"🎵 {MSG_NOT_ADDED}, @{user} 🎵"

    def search(self, query):
        track = None
        response = requests.get(
            f"{API_URL}/search",
            params={
                "q": query,
                "type": "track",
                "limit": 1
            },
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        if response.ok and response.json()["tracks"]["total"] > 0:
            track = response.json()["tracks"]["items"][0]
        return track

    def add_to_playlist(self, track):
        response = requests.post(
            f"{API_URL}/playlists/{self.playlist}/tracks",
            json={"uris": [track["uri"]]},
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
        )
        return response.ok

    def del_last(self, user, users):
        if user not in users or USER_KEY not in users[user]:
            return f"🎵 {MSG_NO_SONG}, @{user} 🎵"
        if self.has_expired():
            self.refresh()
        response = requests.delete(
            f"{API_URL}/playlists/{self.playlist}/tracks",
            json={"tracks": [{"uri": users[user][USER_KEY]}]},
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
        )
        if response.ok:
            users[user].pop(USER_KEY)
        return f"🎵 {MSG_DELETED if response.ok else MSG_NOT_DELETED}, @{user} 🎵"

    def get_playlist_url(self):
        return f"🎵 https://open.spotify.com/playlist/{self.playlist} 🎵"