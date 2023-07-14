import socket

from warp import packet


class Node:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.destination = (self.address, self.port)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def receive(self):
        data = self.socket.recvfrom(2048)
        data, addr = data
        return data, addr

    def send(self, data):
        self.socket.sendto(data, self.destination)
