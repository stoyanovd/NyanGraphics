import random
import socket
import time

from helpers import CommonInterface
from helpers.CommonInterface import GAME_CONF, cell_is_correct
from helpers.Point import Point
from helpers.SettingKeeper import SK

TELEPORTS_NUMBER = 3


class Teleport:
    from_p = Point()
    to_p = Point()


class GameMap:
    def __init__(self):
        self.teleports = []
        a = [(i, j) for i in range(GAME_CONF.FIELD_SIZE) for j in range(GAME_CONF.FIELD_SIZE)]
        for i in range(TELEPORTS_NUMBER):
            t = Teleport()
            t.from_p = Point(a[2 * i])
            t.to_p = Point(a[2 * i + 1])
            self.teleports.append(t)


class ServerSender:
    def __init__(self, room):
        self.room = room
        self.MCAST_PORT = 5007

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    def MCAST_GRP(self, i, j):
        return '.'.join([224, self.room, i, j])

    def send(self, message, i, j):
        self.sock.sendto(message, (self.MCAST_GRP(i, j), self.MCAST_PORT))


class Cat:
    bot_name = 'DEFAULT_RANDOM_BOT'

    def __init__(self, run_number, game_map):
        self.p = Point([random.randint(0, GAME_CONF.FIELD_SIZE - 1) for _ in range(2)])
        self.game_map = game_map
        self.send_to_bot(CommonInterface.pack_init(run_number, game_map, self.p))

    def send_to_bot(self, message):
        pass

    def receive_from_bot(self):
        pass

    # it must be limited by time!!!
    def one_step(self):
        while True:
            direction = random.choice(SK.STEPS.keys())
            if direction == CommonInterface.TELEPORT:
                continue
            np = self.p + SK.STEPS[direction]
            if cell_is_correct(np):
                self.p = np
            yield self.p


class ServerGame:
    def __init__(self):
        self.game_map = GameMap()
        self.sender = ServerSender(1)
        self.run_number = 0
        self.cat = None

    def run(self):
        while True:
            self.run_number += 1
            self.cat = Cat(self.run_number, self.game_map)

            # ---- Send init of game
            for repeat in range(GAME_CONF.REPEATS_NUMBER):
                time_stamp = time.perf_counter()
                self.sender.send(CommonInterface.pack_init(self.run_number, self.game_map, self.cat), 0, 0)
                cur_time = time.perf_counter()
                time.sleep(GAME_CONF.ONE_STEP_TIME_LIMIT_SEC - (cur_time - time_stamp))
            # --------------------

            for t in range(GAME_CONF.STEPS_NUMBER):
                time_stamp = time.perf_counter()
                self.cat.one_step()

                for repeat in range(GAME_CONF.REPEATS_NUMBER):
                    for i in range(GAME_CONF.FIELD_SIZE):
                        for j in range(GAME_CONF.FIELD_SIZE):
                            self.sender.send(self.generate_step(t, i, j), i, j)
                cur_time = time.perf_counter()
                time.sleep(GAME_CONF.ONE_STEP_TIME_LIMIT_SEC - (cur_time - time_stamp))

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
            return [CommonInterface.LEFT, CommonInterface.RIGHT][rx]
        else:
            return [CommonInterface.UP, CommonInterface.DOWN][ry]
