from Irc import *

class ChatBot:

    irc = Irc()
    server = "irc.twitch.tv"
    port = 6667
    tags_cap = "CAP REQ :twitch.tv/tags"
    channel = ""
    nickname = ""
    password = ""
    msg_hi = ""
    msg_bye = ""
    listening = False
    commands = []

    def set_channel(self, channel):
        self.channel = channel

    def set_user(self, nickname, password):
        self.nickname = nickname
        self.password = password

    def set_messages(self, msg_hi, msg_bye):
        self.msg_hi = msg_hi
        self.msg_bye = msg_bye

    def start(self):
        self.irc.connect(self.server, self.port, self.channel, self.nickname, self.password)
        self.irc.send_raw(self.tags_cap)
        self.irc.send(self.channel, self.msg_hi)
        self.listening = True
        while self.listening:
            text = self.irc.get_response()
            if "PRIVMSG" in text and self.channel in text:
                self.parse(text)

    def stop(self):
        self.listening = False
        self.irc.send(self.channel, self.msg_bye)
        self.irc.disconnect()

    def parse(self, text):
        datas = text.split(" ", 4)
        msg = datas[4][1:]
        if msg[:1] == "!":
            tags = self.parse_tags(datas[0])
            username = datas[1].split("!")[0][1:]
            self.parse_command(tags, username, msg)

    def parse_tags(self, str_tags):
        tags = {}
        for tag in str_tags[1:].split(";"):
            tag_pair = tag.split("=")
            tags[tag_pair[0]] = tag_pair[1]
        return tags

    def parse_command(self, tags, username, msg):
        #self.irc.send(self.channel, username + ", which is " + tags["badges"] + ", has sent " + msg)
        command = msg.split()[0][1:]
        if command == "commands":
            self.irc.send(self.channel, "Plus tard, je listerai les commandes ici")
        elif command == "addsong":
            self.irc.send(self.channel, "Plus tard, je pourrai ajouter des chansons à la playlist ici")
        else:
            if command in self.commands:
                self.irc.send(self.channel, "Plus tard, je pourrai exécuter une commande venant d'une liste de commandes")
            else:
                self.irc.send(self.channel, "Cette commande est inconnue")
