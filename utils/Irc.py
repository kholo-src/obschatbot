import select
import socket

DEFAULT_PORT = 6667
TIMEOUT = 1
BUFFER_SIZE = 2048
ENCODING = "utf-8"

class Irc:

    socket = None

    def connect(self, server, port = DEFAULT_PORT):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((server, port))

    def identify(self, nickname, password):
        self.send_raw(f"PASS {password}")
        self.send_raw(f"NICK {nickname}")

    def join(self, channel):
        self.send_raw(f"JOIN {channel}")

    def cap_req(self, cap):
        self.send_raw(f"CAP REQ :{cap}")

    def receive(self):
        rlist, wlist, elist = select.select([self.socket], [], [], TIMEOUT)
        response = None
        if rlist:
            try:
                response = self.socket.recv(BUFFER_SIZE).decode(ENCODING)
                if response.find("PING") != -1:
                    self.send_raw(f"PONG {response.split()[1]}")
            except:
                pass
        return response

    def send(self, channel, msg):
        self.send_raw(f"PRIVMSG {channel} :{msg}")

    def send_raw(self, msg):
        self.socket.send(f"{msg}\n".encode(ENCODING))

    def disconnect(self):
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()