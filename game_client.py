import socket
import struct
from helpers.Point import Point


class Hunter:
    def __init__(self):
        self.p = Point()


BUFFER_SIZE = 10240


class ClientReceiver:
    def __init__(self, room):
        self.room = room

        self.MCAST_PORT = 5007
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def bind_cell(self, i, j):
        self.sock.bind((self.MCAST_GRP(i, j), self.MCAST_PORT))
        mreq = struct.pack("4sl", socket.inet_aton(self.MCAST_GRP(i, j)), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def MCAST_GRP(self, i, j):
        return '.'.join([224, self.room, i, j])

    def recv(self):
        while True:
            self.sock.recv(BUFFER_SIZE)


class ClientGame:
    def __init__(self):
        self.receiver = ClientReceiver(1)
        game_run_is_broken = True
