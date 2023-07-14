from warp import server
from warp import packet
import threading

sock_server = server.Server("127.0.0.1", 5555)

received_packets = 0

@sock_server.on("ping")
def ping(server, data, addr):
    global received_packets
    payload = packet.Packet.decode_packet(data)
    received_packets += 1
    print(f"Ping! {payload}")

@sock_server.on("end")
def ping(server, data, addr):
    print(f"Packet Loss: {100 - (received_packets / 90_000) * 100}%")

sock_server.listen()
