from warp import server
from warp import packet

sock_server = server.Server("127.0.0.1", 5555)


@sock_server.on("ping")
def ping(server, data, addr):
    payload = packet.Packet.decode_packet(data)
    print(f"Ping! {payload}")


sock_server.listen()
