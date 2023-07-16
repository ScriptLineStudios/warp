import socket
import threading
import time

from warp import node
from warp import packet


class Server(node.Node):
    def __init__(self, ip, port):
        super().__init__(ip, port)
        self.socket.bind(self.addr)

        self.connections = {}

        self.handlers = {
            "connection": Server.connection,
        }

    def connection(self, data, addr):
        print(f"[SERVER]: Connecting {addr}")
        self.connections[addr] = {  
            "i": 0,
            "o": 0,
        }

    def send(self, data, addr):
        self.socket.sendto(
            packet.Packet.pack_int(self.connections[addr]["o"]) + data, addr
        )
        self.connections[addr]["o"] += 1

    def receive(self):
        data, addr = self.socket.recvfrom(2048)
        if self.connections.get(addr):  
            acked = chr(data[0])
            data = data[1:]

            _id, data = packet.Packet.read_int(data)

            if self.connections[addr]["i"] <= _id:
                self.connections[addr]["i"] = _id + 1
            else:
                return self.receive()

            return data, addr
        return data, addr

    def on(self, header):
        def inner(func):
            self.handlers[header] = func
            return func

        return inner

    def listen_forever(self):
        while True:
            data, addr = self.receive()
            header, data = packet.Packet.read_string(data)
            self.handlers[header](self, data, addr)

    def listen(self):
        listen_thread = threading.Thread(target=self.listen_forever)
        listen_thread.start()
