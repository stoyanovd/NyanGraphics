import json
import os
import random
import socket
import time
import sys
import sched
import MyLogging
from helpers import CommonInterface as CM
from helpers.CommonInterface import GAME_CONF, cell_is_correct
from helpers.SettingKeeper import SK, Stater
from helpers.TimeoutDecorator import timeout, TimedOutExc
from helpers.TimesConf import TimesConf

TELEPORTS_NUMBER = 3

logger = MyLogging.make_logger()


class GameMap:
    def __init__(self):
        self.teleports = []
        a = [[i, j] for i in range(GAME_CONF.FIELD_SIZE) for j in range(GAME_CONF.FIELD_SIZE)]
        random.shuffle(a)
        for i in range(TELEPORTS_NUMBER):
            self.teleports.append(a[2 * i] + a[2 * i + 1])


class ServerSender:
    def __init__(self, room):
        self.room = room
        self.MCAST_PORT = 5007

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    def MCAST_GRP(self, i, j):
        return '.'.join(map(str, [224, self.room, i, j]))

    def send(self, message, i, j):
        self.sock.sendto(bytes(message, encoding='UTF-8'), (self.MCAST_GRP(i, j), self.MCAST_PORT))
        # logger.info('ServerSender | send to ' + str((i, j)) + ' | msg: ' + message)


class Cat:
    bot_name = 'DEFAULT_RANDOM_BOT'

    def __init__(self, run_number, game_map):
        self.p = [random.randint(0, GAME_CONF.FIELD_SIZE - 1) for _ in range(2)]
        self.run_number = run_number
        self.game_map = game_map
        self.send_to_bot(CM.pack_init(run_number, game_map, self))

        self.time_frame = 1
        self.silly_inner_gen = self.silly_inner_generator()

    # it must be limited by time!!!
    def silly_inner_generator(self):
        while True:
            direction = random.choice(list(SK.STEPS.keys()))
            if direction == CM.TELEPORT:
                continue
            np = (self.p[0] + SK.STEPS[direction][0], self.p[1] + SK.STEPS[direction][1])
            if cell_is_correct(np):
                yield CM.pack_bot_step(self.run_number, self.time_frame, CM.CAT, direction)

    def send_to_bot(self, message):
        logger.debug(message)
        # print(message, file=sys.stdout)
        # we say it straight to our silly generator
        pass

    @timeout(TimesConf.BORDER_DELAY)
    def receive_from_bot(self):
        # ans = input(prompt=sys.stdin) # todo
        ans = next(self.silly_inner_gen)
        ans = json.loads(ans)

        if CM.BOT_STEP in ans.keys():
            assert ans[CM.BOT_STEP][CM.RUN_NUMBER] == self.run_number
            assert ans[CM.BOT_STEP][CM.TIME_FRAME] == self.time_frame
            np = (self.p[0] + SK.STEPS[ans[CM.BOT_STEP][CM.DIRECTION]][0],
                  self.p[1] + SK.STEPS[ans[CM.BOT_STEP][CM.DIRECTION]][1])

            if cell_is_correct(np):
                self.p = np
                return True
        return False

    def one_step(self):
        self.time_frame += 1
        self.send_to_bot(CM.pack_request_for_step(self.run_number, self.time_frame, CM.TELEPORT, self.p))
        self.receive_from_bot()


class ServerGame:
    def __init__(self):
        self.game_map = GameMap()
        self.sender = ServerSender(SK.ROOM_NUMBER)
        self.run_number = 0
        self.cat = None

        self.stater = Stater()
        if not os.path.exists(SK.TO_SERVER_VIS_FIFO):
            open(SK.TO_SERVER_VIS_FIFO, 'w+').close()

        self.send_update_to_server_vis()

    @timeout(TimesConf.BORDER_DELAY)
    def send_update_to_server_vis(self):
        if self.cat:
            self.stater.cat_p = self.cat.p
        try:
            with open(SK.TO_SERVER_VIS_FIFO, 'w') as f:
                json.dump(self.stater.__dict__, f)
        except TimedOutExc:
            return

    def send_init(self):
        self.sender.send(CM.pack_init(self.run_number, self.game_map, self.cat), 0, 0)

    def send_step(self, msg, i, j):
        self.sender.send(msg, i, j)

    def fill_stater(self):
        self.stater.cat_p = self.cat.p

    def run(self):
        while True:
            print('Game Map, start, run_number=' + str(self.run_number))

            self.run_number += 1
            self.cat = Cat(self.run_number, self.game_map)

            self.send_update_to_server_vis()

            s = sched.scheduler(time.perf_counter, time.sleep)

            for repeat in range(GAME_CONF.REPEATS_NUMBER):
                s.enter(TimesConf.BORDER_DELAY + repeat * TimesConf.BETWEEN_REPEATS_DT, 1, self.send_init)
            s.enter(TimesConf.TOTAL, 0, lambda *args: None)

            s.run()

            for t in range(GAME_CONF.STEPS_NUMBER):
                logger.info('Cat, start, time_frame=' + str(self.cat.time_frame) + ', p=' + str(self.cat.p))

                self.send_update_to_server_vis()

                s = sched.scheduler(time.perf_counter, time.sleep)

                s.enter(0, 2, self.cat.one_step)

                for i in range(GAME_CONF.FIELD_SIZE):
                    for j in range(GAME_CONF.FIELD_SIZE):
                        to_cat_direction = self.generate_step(t, i, j)
                        msg = CM.pack_bot_step(self.run_number, self.cat.time_frame, CM.CAT, to_cat_direction)
                        for repeat in range(GAME_CONF.REPEATS_NUMBER):
                            s.enter(TimesConf.BORDER_DELAY + repeat * TimesConf.BETWEEN_REPEATS_DT, 1,
                                    self.send_step, argument=(msg, i, j))

                s.enter(TimesConf.TOTAL, 0, lambda *args: None)
                s.run()

    def generate_step(self, t, i, j):
        return self.make_direction(i, j)

    def make_direction(self, i, j):
        dx = abs(i - self.cat.p[0])
        rx = int(i < self.cat.p[0])
        dy = abs(j - self.cat.p[1])
        ry = int(j < self.cat.p[1])

        if dx == dy and dx == 0:
            return CM.HERE

        d = dx > dy
        if dx == dy:
            d = random.randint(0, 1)

        if d:
            return [CM.LEFT, CM.RIGHT][rx]
        else:
            return [CM.UP, CM.DOWN][ry]


def main_server():
    ServerGame().run()


if __name__ == '__main__':
    main_server()
