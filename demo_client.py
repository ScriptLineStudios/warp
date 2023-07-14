from warp import client
from warp import packet

import time

sock_client = client.Client("127.0.0.1", 5555)
sock_client.connect()

for x in range(90_000):
    sock_client.send(
        bytes(packet.Packet(sock_client, "ping", {"some_random_data": x, 34: 45}))
    )
    print(f"Sending: {x}")

sock_client.send(
    bytes(packet.Packet(sock_client, "end", {})), reliable=True
)
