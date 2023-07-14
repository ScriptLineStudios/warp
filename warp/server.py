import socket
import threading
import time

from warp import node
from warp import packet


class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.addr = (self.ip, self.port)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(self.addr)

        self.handlers = {
            "connection": Server.connection,
        }

        self.connections = {}

    def connection(self, data, addr):
        print(f"[SERVER]: Connecting {addr}")
        self.connections[
            addr
        ] = {  # From this point onward, all received packets from this address will require an id
            "i": 0,
            "o": 0,
        }

    def send(self, data, addr):
        self.socket.sendto(
            packet.Packet.pack_int(self.connections[addr]["o"]) + data, addr
        )
        self.connections[addr]["o"] += 1

    def receive(self):
        data, addr = self.socket.recvfrom(20480)
        if self.connections.get(
            addr
        ):  # If we have already registered the connection, we must demand an id.
            is_reliable = chr(data[0])                
            data = data[1:]

            _id, data = packet.Packet.read_int(data)
            if is_reliable == "R": # If the packet is reliable we must immediately let the client know we received it.
                print("Packet is reliable, telling the client we received it.")
                self.send(bytes(packet.Packet(self, "reliable", {"id": _id})), addr)            
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
