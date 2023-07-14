import socket

class Connection:
    def __init__(self, addr):
        self.addr = addr

    def recv(self):
        