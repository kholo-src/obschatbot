from helpers.TwitchIrc import TwitchIrc

MSG_HELP = "Je connais les commandes suivantes :"
MSG_CANT_STOP = "Personne ne peut m'arrêter !"
MSG_STOP = "Oh non..."
MSG_UNKNOWN_CMD = "Je ne connais pas cette commande"

class ChatBot:

    twitch_irc = TwitchIrc()

    services = []
    users = {}

    msg_hi = ""
    msg_bye = ""

    running = False

    # Settings -----

    def set_twitch_irc_settings(self, nickname, password, channel):
        self.twitch_irc.join(nickname, password, channel)

    def add_service(self, service):
        self.services.append(service)

    def clear_services(self):
        self.services = []
    
    def set_welcome_message(self, message):
        self.msg_hi = message

    def set_farewell_message(self, message):
        self.msg_bye = message

    # Commands -----

    def parse_response(self, response):
        command = response["message"].split(" ", 1)[0][1:]
        if command == "help":
            self.display_help()
            return
        elif command == "stop":
            self.stop_command(response["tags"]["badges"])
            return
        result = None
        for service in self.services:
            if not service.knows(command):
                continue
            result = service.eval(command, response, self.users)
        if result:
            self.twitch_irc.send(result)
        else:
            self.twitch_irc.send(MSG_UNKNOWN_CMD)

    def display_help(self):
        self.twitch_irc.send(f"{MSG_HELP}{self.list_commands()}")

    def list_commands(self):
        commands = ["help"]
        for service in self.services:
            commands.extend(service.list_commands())
        return f" !{' !'.join(commands)}"

    def stop_command(self, badges):
        for badge in badges:
            if badge["name"] == "broadcaster":
                self.twitch_irc.send(MSG_STOP)
                self.stop()
                return
        self.twitch_irc.send(MSG_CANT_STOP)

    # Listening -----

    def start(self):
        for service in self.services:
            service.start()
        self.twitch_irc.request_tags()
        self.twitch_irc.start()
        if self.msg_hi != "":
            self.twitch_irc.send(self.msg_hi)
        self.running = True
        while self.running:
            response = self.twitch_irc.receive()
            if response and response["message"][:1] == "!":
                self.parse_response(response)

    def stop(self):
        self.running = False
        if self.msg_bye != "":
            self.twitch_irc.send(self.msg_bye)
        self.twitch_irc.stop()
        for service in self.services:
            service.stop()
