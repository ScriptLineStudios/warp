import struct
import hashlib


def _hash(x):
    return (
        int(hashlib.md5(str(x).encode()).hexdigest(), 16)
        // 2053989096583912534982262679
    )


type_map = {
    _hash(str): str,
    _hash(int): int,
    _hash(float): float,
}


class Packet:
    @staticmethod
    def read_int(buffer):
        data = struct.unpack_from("!q", buffer, 0)[0]
        buffer = buffer[struct.calcsize("!q") :]
        return data, buffer

    @staticmethod
    def read_string(buffer):
        size = struct.unpack_from("i", buffer, 0)[0]
        buffer = buffer[struct.calcsize("i") :]
        string = ""
        for i in range(size):
            string += struct.unpack_from("c", buffer, 0)[0].decode()
            buffer = buffer[struct.calcsize("c") :]
        return string, buffer

    @staticmethod
    def read_float(buffer):
        data = struct.unpack_from("!f", buffer, 0)[0]
        buffer = buffer[struct.calcsize("!f") :]
        return data, buffer

    @staticmethod
    def pack_string(data):
        buf = struct.pack(
            f"i{'c' * len(data)}", len(data), *[char.encode("utf-8") for char in data]
        )
        return buf

    @staticmethod
    def pack_int(data):
        return struct.pack("!q", data)

    @staticmethod
    def pack_float(data):
        return struct.pack("!f", data)

    @staticmethod
    def pack_type(data):
        tp = type(data)
        tp_byte = Packet.pack_int(_hash(tp))

        if tp == str:
            return tp_byte + Packet.pack_string(data)
        elif tp == int:
            return tp_byte + Packet.pack_int(data)
        elif tp == float:
            return tp_byte + Packet.pack_float(data)

    @staticmethod
    def read_type(data):
        tp, data = Packet.read_int(data)
        tp = type_map[tp]

        if tp == str:
            return Packet.read_string(data)
        elif tp == int:
            return Packet.read_int(data)
        elif tp == float:
            return Packet.read_float(data)

    @staticmethod
    def decode_packet(data):
        payload = {}
        while len(data) > 0:
            key, data = Packet.read_type(data)
            value, data = Packet.read_type(data)
            payload[key] = value
        return payload

    def __init__(self, node, tp, payload):
        self.node = node
        self.tp = tp
        self.payload = payload

    def __bytes__(self):
        tp = self.pack_string(self.tp)

        for key in self.payload.keys():
            tp += self.pack_type(key)
            tp += self.pack_type(self.payload[key])

        return tp
