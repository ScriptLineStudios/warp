import socket
import queue
import threading

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

        self.reliable_stream = {}
        self.handlers = {
            "reliable": self.reliable_response,
        }

    @staticmethod
    def reliable_response(self, data, addr):
        payload = packet.Packet.decode_packet(data)
        print("GOT RELIABLE RESPONSE")
        print(payload["id"])
        _id = payload["id"]
        del self.reliable_stream[_id] #We got the id. We can now remove the packet from the dictionary

    def send(self, data, reliable=False):
        if not reliable:
            self.socket.sendto(b'N' + packet.Packet.pack_int(self.o) + data, self.addr)
        else:
            print("Sending reliable message...")
            self.socket.sendto(b'R' + packet.Packet.pack_int(self.o) + data, self.addr)
            self.reliable_stream[self.o] = {"data": data, "time": 0}

        self.o += 1

    def handle_reliable_messages(self):
        while True:
            if self.reliable_stream:
                print(self.reliable_stream)
            for _id in self.reliable_stream.keys():    
                self.reliable_stream[_id]["time"] += 1
                if self.reliable_stream[_id]["time"] >= 90000:
                    # self.socket.sendto(b'R' + packet.Packet.pack_int(self.o) + self.reliable_stream[_id]["data"], self.addr)
                    self.reliable_stream[_id]["time"] = 0

    def manage_reliable_stream(self):
        reliable_thread = threading.Thread(target=self.handle_reliable_messages)
        reliable_thread.start()

    def receive(self):
        data, addr = self.socket.recvfrom(20480)
        _id, data = packet.Packet.read_int(data)
        if self.i <= _id:
            self.i = _id + 1
        else:
            return self.receive()

        return data, addr

    def listen_forever(self):
        while True:
            data, addr = self.receive()
            header, data = packet.Packet.read_string(data)
            self.handlers[header](self, data, addr)

    def listen(self):
        listen_thread = threading.Thread(target=self.listen_forever)
        listen_thread.start()

    def connect(self):
        connection = packet.Packet(self, "connection", {})
        self.socket.sendto(bytes(connection), self.addr)
        self.listen()
        self.manage_reliable_stream()