from CommandManager import *
from Spotify import *
from Twitch import *
import random
import re

MSG_HELP_FR = "Je connais les commandes suivantes : !aide !help !cmd !addsong !<n>d<f> (n = nombre de dés, f = nombre de faces)"
MSG_HELP_EN = "I know the following commands: !aide !help !cmd !addsong !<n>d<f> (n = dices number, f = faces number)"
MSG_REFUSE = "Je ne connais pas cette commande, "
PATTERN_ARGS = "\{[0-9]+\}"
PATTERN_DICE = "^([0-9]+)d([0-9]+)$"

class ChatBot:

    spotify = Spotify()
    twitch = Twitch()

    msg_hi = ""
    msg_bye = ""

    playlist_id = ""
    spotify_code = ""

    started = False
    commands = CommandManager()

    # Settings -----

    def set_command_file(self, cmd_file):
        self.commands.set_file(cmd_file)

    def set_messages(self, msg_hi, msg_bye):
        self.msg_hi = msg_hi
        self.msg_bye = msg_bye

    def set_twitch_settings(self, channel, username, password):
        self.twitch.set_channel(channel)
        self.twitch.set_user(username, password)

    def set_spotify_settings(self, playlist_id, client_id, client_secret):
        self.playlist_id = playlist_id
        self.spotify.set_credentials(client_id, client_secret)

    def set_spotify_code(self, code):
        self.spotify_code = code

    def set_spotify_refresh_token(self, token):
        self.spotify.refresh_token = token

    # Helpers -----

    def get_spotify_code_url(self):
        return self.spotify.get_authorization_url()

    def authorize_spotify(self):
        return self.spotify.authorize(self.spotify_code)

    # Commands -----

    def display_help(self, keyword):
        additional_commands = ""
        for command in self.commands.list():
            additional_commands = additional_commands + " !" + command
        if keyword == "aide":
            self.twitch.send(MSG_HELP_FR + additional_commands)
        elif keyword == "help":
            self.twitch.send(MSG_HELP_EN + additional_commands)

    def stop_command(self, badges):
        if not self.twitch.is_broadcaster(badges):
            self.twitch.send("Personne ne peut m'arrêter !")
        else:
            self.twitch.send("Oh non...")
            self.stop()

    def manage_commands(self, response):
        if not self.twitch.is_moderator(response["badges"]):
            self.twitch.send("Il faut être modérateur pour gérer les commandes, @" + response["username"])
            return
        components = response["message"].split(" ", 3)
        if components[1] == "add" or components[1] == "edit" or components[1] == "update":
            self.commands.add_command(components[2], components[3])
            self.twitch.send("La commande !" + components[2] + " a été ajoutée, @" + response["username"])
        elif components[1] == "del" or components[1] == "delete" or components[1] == "remove":
            if not self.commands.has(components[2]):
                self.twitch.send("Cette commande n'existe pas, @" + response["username"])
                return
            self.commands.del_command(components[2])
            self.twitch.send("La commande !" + components[2] + " a été supprimée, @" + response["username"])

    def add_song(self, message):
        components = message.split(" ", 1)
        if len(components) < 2:
            self.twitch.send("Utilisation: !addsong <critères de recherches>")
            return
        query = components[1]
        track = self.spotify.search(query)
        if track is None:
            self.twitch.send("Aucun titre trouvé :(")
            return
        if self.spotify.add_to_playlist(self.playlist_id, track):
            artist = track["artists"][0]["name"]
            title = track["name"]
            self.twitch.send("Le morceau '" + title + "' de " + artist + " a été ajouté")
        else:
            self.twitch.send("Le morceau n'a pas pu être ajouté")

    def custom_command(self, message):
        components = message.split(" ", 1)
        command = self.commands.get(components[0][1:])
        args = list(dict.fromkeys(re.findall(PATTERN_ARGS, command)))
        args.sort()
        count = len(args)
        if count >= 1:
            msg_components = []
            if len(components) > 1:
                msg_components = components[1].split(" ")
            if len(msg_components) != count:
                self.twitch.send("La commande n'est pas complète.")
                return
            for i in range(0, count):
                command = command.replace(args[i], msg_components[i])
            self.twitch.send(command)
        else:
            self.twitch.send(command)

    def launch_dices(self, number, size):
        dices = []
        for i in range(0, number):
            dices.append(str(random.randint(1, size)))
        self.twitch.send("Vous avez obtenu : " + " + ".join(dices))

    def refuse(self, username):
        self.twitch.send(MSG_REFUSE + "@" + username)

    # Listening -----

    def start(self):
        self.commands.load()
        self.spotify.refresh()
        self.twitch.start()
        self.twitch.send(self.msg_hi)
        self.started = True
        while self.started:
            response = self.twitch.get_response()
            if len(response) > 0 and response["message"][:1] == "!":
                self.eval_command(response)

    def eval_command(self, response):
        command = response["message"].split(" ", 1)[0][1:]
        m = re.match(PATTERN_DICE, command)
        if command == "aide" or command == "help":
            self.display_help(command)
        elif command == "stop":
            self.stop_command(response["badges"])
        elif command == "cmd":
            self.manage_commands(response)
        elif command == "addsong":
            self.add_song(response["message"])
        elif self.commands.has(command):
            self.custom_command(response["message"])
        elif m:
            self.launch_dices(int(m.group(1)), int(m.group(2)))
        else:
            self.refuse(response["username"])

    def stop(self):
        self.started = False
        self.twitch.send(self.msg_bye)
        self.twitch.stop()
