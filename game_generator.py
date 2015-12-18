import pickle
import random

from helpers.CommonInterface import GAME_CONF
from helpers.Point import Point
from helpers.SettingKeeper import SK


def cell_is_correct(p):
    return (0 < p.x <= SK.FIELD_SIZE) and (0 < p.y <= SK.FIELD_SIZE)


class GameMap:
    def __init__(self, teleports=None):
        self.teleports = teleports


assert SK.FIELD_SIZE > 5


class ServerSender:
    def __init__(self):
        import socket

        self.MCAST_GRP = '224.1.1.1'
        self.MCAST_PORT = 5007

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    def send(self):
        self.sock.sendto("robot", (self.MCAST_GRP, self.MCAST_PORT))

    def send_init(self):
        pass

    def send_step(self):
        pass


class Cat:
    bot_name = 'DEFAULT_RANDOM_BOT'

    def __init__(self):
        self.p = Point([5, 5])

    def one_step(self):
        while True:
            direction = random.choice(SK.STEPS.keys())
            if direction == SK.TELEPORT:
                continue
            np = self.p + SK.STEPS[direction]
            if cell_is_correct(np):
                self.p = np
            yield self.p


class ServerGame:
    def __init__(self):
        self.game_map = GameMap()
        self.cat = Cat()
        self.sender = ServerSender()
        self.run_number = 0

    def run(self):
        while True:
            self.run_number += 1
            self.sender.send(self.generate_init(self.run_number))
            s

            for t in range(GAME_CONF.STEPS_NUMBER):
                self.cat.one_step()
                for repeat in range(GAME_CONF.REPEATS_NUMBER):
                    for i in range(SK.FIELD_SIZE):
                        for j in range(SK.FIELD_SIZE):
                            self.sender.send(self.generate_step(t, i, j))

    def generate_init(self):
        return pickle.dumps([self.game_map, self.cat])

    def generate_step(self, t, i, j):
        return self.make_direction(i, j)

    def make_direction(self, i, j):
        dx = abs(i - self.cat.p.x)
        rx = int(i > self.cat.p.x)
        dy = abs(j - self.cat.p.y)
        ry = int(j > self.cat.p.y)

        d = dx < dy
        if dx == dy:
            d = random.randint(0, 1)

        if d:
            return [SK.LEFT, SK.RIGHT][rx]
        else:
            return [SK.UP, SK.DOWN][ry]

# def recv(self):
#     import socket
#     import struct
#
#     MCAST_GRP = '224.1.1.1'
#     MCAST_PORT = 5007
#
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
#     sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     sock.bind(('', MCAST_PORT))  # use MCAST_GRP instead of '' to listen only
#     # to MCAST_GRP, not all groups on MCAST_PORT
#     mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
#
#     sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
#
#     while True:
#         print
#         sock.recv(10240)
