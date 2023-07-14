import socket

from warp import node
from warp import packet


class Client:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.addr = (self.ip, self.port)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.i = 0
        self.o = 0

    def send(self, data):
        self.socket.sendto(packet.Packet.pack_int(self.o) + data, self.addr)
        self.o += 1

    def receive(self):
        data, addr = self.socket.recvfrom(20480)
        _id, data = packet.Packet.read_int(data)
        if self.i <= _id:
            self.i = _id + 1
        else:
            return self.receive()

        return data, addr

    def connect(self):
        connection = packet.Packet(self, "connection", {})
        self.socket.sendto(bytes(connection), self.addr)
