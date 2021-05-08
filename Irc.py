import socket
import time

class Irc:

    irc = socket.socket()
    channel = ""

    def __init__(self):
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send_raw(self, msg):
        self.irc.send(bytes(msg + "\n", "UTF-8"))

    def connect(self, server, port, username, password):
        self.irc.connect((server, port))
        self.send_raw("PASS " + password)
        self.send_raw("NICK " + username)

    def join(self, channel):
        self.channel = "#" + channel
        self.send_raw("JOIN " + self.channel)

    def send(self, msg):
        self.send_raw("PRIVMSG " + self.channel + " :" + msg)

    def get_response(self):
        time.sleep(1)
        response = self.irc.recv(2040).decode("UTF-8")
        if response.find("PING") != -1:
            self.send_raw("PONG " + response.split()[1])
        return response

    def disconnect(self):
        self.irc.close()
