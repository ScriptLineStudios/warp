from warp import client
from warp import packet

sock_client = client.Client("127.0.0.1", 5555)
sock_client.connect()
for x in range(1000000):
    sock_client.send(
        bytes(packet.Packet(sock_client, "ping", {"some_random_data": x, 34: 45}))
    )