from utils.Irc import Irc

SERVER = "irc.twitch.tv"
PORT = 6667
CAP_URI = "twitch.tv"

class TwitchIrc:

    irc = Irc()
    nickname = ""
    password = ""
    channel = ""
    capabilities = {"membership": False, "tags": False, "commands": False}

    def join(self, nickname, password, channel):
        self.nickname = nickname
        self.password = password
        self.channel = f"#{channel}"

    def request_membership(self):
        self.capabilities["membership"] = True

    def request_tags(self):
        self.capabilities["tags"] = True

    def request_commands(self):
        self.capabilities["commands"] = True

    def start(self):
        self.irc.connect(SERVER, PORT)
        self.irc.identify(self.nickname, self.password)
        self.irc.join(self.channel)
        for cap, req in self.capabilities.items():
            if req:
                self.irc.cap_req(f"{CAP_URI}/{cap}")

    def receive(self):
        response = self.irc.receive()
        if not response:
            return
        if "PRIVMSG" in response and self.channel in response:
            return self.parse(response)

    def parse(self, response_str):
        response = {}
        components = response_str.split(" ", 4 if self.capabilities["tags"] else 3)
        response["username"] = components[1 if self.capabilities["tags"] else 0].split("!")[0][1:]
        response["message"] = components[4 if self.capabilities["tags"] else 3][1:].strip()
        if self.capabilities["tags"]:
            response["tags"] = self.parse_tags(components[0][1:])
        return response

    def parse_tags(self, tags_str):
        tags = {}
        for tag in tags_str.split(";"):
            name, value = tag.split("=")
            if name == "badge-info":
                if value != "":
                    value = self.parse_badge(value)
                else:
                    value = None
            elif name in ["badges", "emotes"]:
                value = value.split(",")
                if name == "badges":
                    badges = []
                    if value != [""]:
                        for badge in value:
                            badges.append(self.parse_badge(badge))
                        value = badges
                    else:
                        value = []
            tags[name] = value
        return tags

    def parse_badge(self, badge_str):
        name, value = badge_str.split("/")
        return {"name": name, "value": value}

    def send(self, msg):
        self.irc.send(self.channel, msg)

    def stop(self):
        self.irc.disconnect()
