import socket
import time

class Irc:

    irc = socket.socket()

    def __init__(self):
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, server, port, channel, nickname, password):
        self.irc.connect((server, port))
        self.irc.send(bytes("PASS " + password + "\n", "UTF-8"))
        self.irc.send(bytes("NICK " + nickname + "\n", "UTF-8"))
        self.irc.send(bytes("JOIN " + channel + "\n", "UTF-8"))

    def disconnect(self):
        self.irc.close()

    def send_raw(self, raw):
        self.irc.send(bytes(raw + "\n", "UTF-8"))

    def send(self, channel, msg):
        self.irc.send(bytes("PRIVMSG " + channel + " :" + msg + "\n", "UTF-8"))

    def get_response(self):
        time.sleep(1)
        resp = self.irc.recv(2040).decode("UTF-8")
        if resp.find("PING") != -1:
            self.irc.send(bytes("PONG " + resp.split()[1] + "\r\n", "UTF-8"))
        return resp
