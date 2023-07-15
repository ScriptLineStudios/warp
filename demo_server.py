from warp import server
from warp import packet
import threading

sock_server = server.Server("127.0.0.1", 5555)
number = 300000

received_packets = 0

@sock_server.on("ping")
def ping(server, data, addr):
    global received_packets
    payload = packet.Packet.decode_packet(data)
    print(payload)
    received_packets += 1


@sock_server.on("end")
def ping(server, data, addr):
    print(f" --- Transmission of {number} packets complete. --- ")
    print(f"Packet Loss: {100 - (received_packets / number) * 100}%")


sock_server.listen()
