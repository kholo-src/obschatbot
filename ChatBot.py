from Spotify import *
from Twitch import *

MSG_HELP_FR = "Je connais les commandes suivantes : !aide !help !cmd !addsong"
MSG_HELP_EN = "I know the following commands: !aide !help !cmd !addsong"
MSG_REFUSE = "Je ne connais pas cette commande, "

class ChatBot:

    twitch = Twitch()
    spotify = Spotify()

    msg_hi = ""
    msg_bye = ""
    spotify_client_id = ""
    spotify_client_secret = ""
    spotify_playlist_id = ""

    cmd_file = ""
    started = False
    commands = []

    # Settings -----

    def set_command_file(self, cmd_file):
        self.cmd_file = cmd_file

    def set_messages(self, msg_hi, msg_bye):
        self.msg_hi = msg_hi
        self.msg_bye = msg_bye

    def set_twitch_settings(self, channel, username, password):
        self.twitch.set_channel(channel)
        self.twitch.set_user(username, password)

    def set_spotify_settings(self, client_id, client_secret, playlist_id):
        self.spotify_client_id = client_id
        self_spotify_client_secret = client_secret
        self_spotify_playlist_id = playlist_id

    # Commands -----

    def display_help(self, command):
        if command == "aide":
            self.twitch.send(MSG_HELP_FR)
        elif command == "help":
            self.twitch.send(MSG_HELP_EN)

    def manage_commands(self, response):
        self.twitch.send("Ici je pourrai traiter les commandes de gestion des commandes")

    def add_song(self, query):
        if len(query) == 1:
            self.twitch.send("Utilisation de la commande: !addsong Titre")
        else:
            self.twitch.send("Ici je pourrai ajouter des chansons à la liste de lecture")

    def custom_command(self, response):
        self.twitch.send("Ici je traiterai les commandes personnalisées")

    def refuse(self, username):
        self.twitch.send(MSG_REFUSE + "@" + username)

    # Listening -----

    def start(self):
        self.twitch.start()
        self.twitch.send(self.msg_hi)
        self.started = True
        while self.started:
            response = self.twitch.get_response()
            if len(response) > 0 and response["message"][:1] == "!":
                self.eval_command(response)

    def eval_command(self, response):
        command = response["message"].split(" ", 1)[0][1:].strip()
        if command == "aide" or command == "help":
            self.display_help(command)
        elif command == "cmd":
            self.manage_commands(response)
        elif command == "addsong":
            self.add_song(response["message"].split(" ", 1))
        elif command in self.commands:
            self.custom_command(response)
        else:
            self.refuse(response["username"])

    def stop(self):
        self.started = False
        self.twitch.send(self.msg_bye)
        self.twitch.stop()
