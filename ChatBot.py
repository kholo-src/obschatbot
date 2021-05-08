from CommandManager import *
from Spotify import *
from Twitch import *
import re

MSG_HELP_FR = "Je connais les commandes suivantes : !aide !help !cmd !addsong"
MSG_HELP_EN = "I know the following commands: !aide !help !cmd !addsong"
MSG_REFUSE = "Je ne connais pas cette commande, "
PATTERN_ARGS = "\{[0-9]+\}"

class ChatBot:

    twitch = Twitch()
    spotify = Spotify()

    msg_hi = ""
    msg_bye = ""
    spotify_client_id = ""
    spotify_client_secret = ""
    spotify_playlist_id = ""

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

    def set_spotify_settings(self, client_id, client_secret, playlist_id):
        self.spotify_client_id = client_id
        self_spotify_client_secret = client_secret
        self_spotify_playlist_id = playlist_id

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

    def add_song(self, query):
        if len(query) == 1:
            self.twitch.send("Utilisation de la commande: !addsong Titre")
        else:
            self.twitch.send("Ici je pourrai ajouter des chansons à la liste de lecture")

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

    def refuse(self, username):
        self.twitch.send(MSG_REFUSE + "@" + username)

    # Listening -----

    def start(self):
        self.commands.load()
        self.twitch.start()
        self.twitch.send(self.msg_hi)
        self.started = True
        while self.started:
            response = self.twitch.get_response()
            if len(response) > 0 and response["message"][:1] == "!":
                self.eval_command(response)

    def eval_command(self, response):
        command = response["message"].split(" ", 1)[0][1:]
        if command == "aide" or command == "help":
            self.display_help(command)
        elif command == "stop":
            self.stop_command(response["badges"])
        elif command == "cmd":
            self.manage_commands(response)
        elif command == "addsong":
            self.add_song(response["message"].split(" ", 1))
        elif self.commands.has(command):
            self.custom_command(response["message"])
        else:
            self.refuse(response["username"])

    def stop(self):
        self.started = False
        self.twitch.send(self.msg_bye)
        self.twitch.stop()
