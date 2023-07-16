from warp import client
from warp import packet

import time

sock_client = client.Client("127.0.0.1", 5555)
sock_client.connect()

for i in range(10000):
    sock_client.send(
        bytes(packet.Packet(sock_client, "ping", {"some_random_data": 100, i: 45})),
        reliable=False,
    )

sock_client.send(
    bytes(packet.Packet(sock_client, "end", {})),
    reliable=True,
)