from Irc import *

TWITCH_IRC_HOST = "irc.twitch.tv"
TWITCH_IRC_PORT = 6667
TWITCH_TAGS_CAP = "CAP REQ :twitch.tv/tags"

class Twitch:

    irc = Irc()
    channel = ""
    username = ""
    password = ""

    def set_channel(self, channel):
        self.channel = channel

    def set_user(self, username, password):
        self.username = username
        self.password = password

    def start(self):
        self.irc.connect(TWITCH_IRC_HOST, TWITCH_IRC_PORT, self.username, self.password)
        self.irc.join(self.channel)
        self.irc.send_raw(TWITCH_TAGS_CAP)

    def send(self, msg):
        self.irc.send(msg)

    def get_response(self):
        response = {}
        text = self.irc.get_response()
        if "PRIVMSG" in text and "#" + self.channel in text:
            response = self.parse_response(text)
        return response

    def parse_response(self, response):
        raw = response.split(" ", 4)
        return {
            "username": raw[1].split("!")[0][1:],
            "badges": self.parse_badges(self.parse_tags(raw[0])),
            "message": raw[4][1:]
        }
    def parse_tags(self, raw):
        tags = {}
        for component in raw.split(";"):
            tag = component.split("=", 1)
            tags[tag[0]] = tag[1]
        return tags

    def parse_badges(self, tags):
        badges = []
        for badge in tags["badges"].split(","):
            badges.append(badge.split("/", 1)[0])
        return badges

    def stop(self):
        self.irc.disconnect()
