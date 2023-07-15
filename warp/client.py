import socket
import queue
import threading
import time

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

        self.handlers = {}
        self.reliable_queue = queue.Queue()
        self.reliable_packet_register = {}

    def reliable(self, data):
        try:
            data, addr = self.reliable_queue.get(timeout=15) # Block until we receive an okay! or timeout and have to send a new packet!
            payload = packet.Packet.decode_packet(data)
            _id = payload["id"]
            self.reliable_packet_register[_id] = True
            print(f"Received reliable response: {_id}")
        except queue.Empty:
            print("resending...")
            self.socket.sendto(b"R" + packet.Packet.pack_int(self.o) + data, self.addr)
            self.reliable_packet_register[self.o] = False
            # self.reliable(data)
            threading.Thread(target=self.reliable, args=(data, )).start()

    def send(self, data, reliable=False):
        if not reliable:
            self.socket.sendto(b"N" + packet.Packet.pack_int(self.o) + data, self.addr)
        else:
            print(f"Sending reliable message: {self.o}")
            self.socket.sendto(b"R" + packet.Packet.pack_int(self.o) + data, self.addr)
            self.reliable_packet_register[self.o] = False
            # self.reliable(data)
            threading.Thread(target=self.reliable, args=(data, )).start()


        self.o += 1

    def receive(self):
        data, addr = self.socket.recvfrom(2048)
        _id, data = packet.Packet.read_int(data)
        if self.i <= _id:
            self.i = _id + 1
        else:
            return self.receive()

        return data, addr

    def listen_forever(self):
        while True:
            data, addr = self.receive()  # This recv is already blocking...
            header, data = packet.Packet.read_string(data)
            if header == "reliable":
                self.reliable_queue.put((data, addr))
            else:
                self.handlers[header](self, data, addr)

    def listen(self):
        listen_thread = threading.Thread(target=self.listen_forever)
        listen_thread.start()

    def connect(self):
        connection = packet.Packet(self, "connection", {})
        self.socket.sendto(bytes(connection), self.addr)
        self.listen()
