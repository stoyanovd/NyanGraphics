import json
import logging
import random
import sched
import socket
import struct
import time
import sys
from game_server import GameMap
from helpers import CommonInterface as CM
from helpers.CommonInterface import cell_is_correct
from helpers.SettingKeeper import SK
from helpers.TimeoutDecorator import timeout, TimedOutExc
from helpers.TimesConf import TimesConf

BUFFER_SIZE = 10240
CLIENT_DELAY_BETWEEN_CHECKS = 0.05

logging.basicConfig(level=logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger = logging.getLogger("__CLIENT__")
logger.addHandler(ch)


class ClientReceiver:
    def __init__(self, room):
        self.room = room
        self.MCAST_PORT = 5007
        self.sock = None

    def bind_cell(self, i, j):
        logger.info('want to bind: ' + str((self.MCAST_GRP(i, j), self.MCAST_PORT)))
        if self.sock:
            self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.MCAST_GRP(i, j), self.MCAST_PORT))
        mreq = struct.pack("4sl", socket.inet_aton(self.MCAST_GRP(i, j)), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def MCAST_GRP(self, i, j):
        return '.'.join(map(str, [224, self.room, i, j]))

    def recv(self, only_init):
        while True:
            d = self.sock.recv(BUFFER_SIZE)
            d = bytes.decode(d, encoding='UTF-8')
            logger.info('recv from Server: ' + d)
            d = json.loads(d)
            if CM.INIT in d:
                return d
            if only_init:
                continue
            assert CM.BOT_STEP in d
            return d


class Hunter:
    def __init__(self):
        self.p = 0, 0
        self.game_run = None
        self.cat_direction = CM.LEFT # todo fix it, please
        self.time_frame = 0
        self.silly_gen = self.silly_inner_hunter()

    def start_new_game_run(self, d_init):
        self.game_run = GameRun(d_init)
        self.p = [random.randint(0, self.game_run.field_size - 1) for _ in range(2)]

    def silly_inner_hunter(self):
        while True:
            yield CM.pack_bot_step(self.game_run.run_number, self.time_frame, CM.HUNTER, self.cat_direction)

    def send_to_bot(self, message):
        print(message, file=sys.stdout)
        # our silly bot straightly get it all

    @timeout(TimesConf.BORDER_DELAY)
    def receive_from_bot(self):
        try:
            # ans = input(prompt=sys.stdin) # todo
            ans = next(self.silly_gen)
            ans = json.loads(ans)
            if CM.BOT_STEP in ans:
                assert ans[CM.BOT_STEP][CM.RUN_NUMBER] == self.game_run.run_number
                assert ans[CM.BOT_STEP][CM.TIME_FRAME] == self.time_frame
                np = (self.p[0] + SK.STEPS[ans[CM.BOT_STEP][CM.DIRECTION]][0],
                      self.p[1] + SK.STEPS[ans[CM.BOT_STEP][CM.DIRECTION]][1])
                if cell_is_correct(np):
                    self.p = np
                    return True
            return False
        except TimedOutExc:
            return False

    def process_step(self):
        if self.game_run is None:
            return
        self.send_to_bot(
            CM.pack_request_for_step(self.game_run.run_number, self.time_frame, self.cat_direction, self.p))
        self.receive_from_bot()


class ClientGame:
    def __init__(self):
        self.receiver = ClientReceiver(1)
        self.hunter = Hunter()

        self.receiver.bind_cell(0, 0)
        d = self.receiver.recv(only_init=True)
        d = d[CM.INIT]
        self.hunter.start_new_game_run(d)

    @timeout(TimesConf.TOTAL - 2 * TimesConf.BORDER_DELAY)
    def receivings_msgs(self):
        try:
            while True:
                if self.hunter.game_run is None:
                    self.receiver.bind_cell(0, 0)
                    d = self.receiver.recv(only_init=True)
                else:
                    self.receiver.bind_cell(self.hunter.p[0], self.hunter.p[1])
                    d = self.receiver.recv(only_init=False)

                if CM.BOT_STEP in d:
                    assert CM.CAT == d[CM.BOT_STEP][CM.WHOIS]
                    if d[CM.BOT_STEP][CM.RUN_NUMBER] != self.hunter.game_run.run_number:
                        self.hunter.game_run = None  # ATTENTION!
                    if d[CM.BOT_STEP][CM.TIME_FRAME] - self.hunter.time_frame > 1:
                        self.hunter.game_run = None  # ATTENTION!
                    self.hunter.cat_direction = d[CM.BOT_STEP][CM.DIRECTION]
                    if self.hunter.cat_direction == CM.HERE:
                        logger.info("----- HOORAY!!!!")
                        logger.info("-----             We catch him!")
                        logger.info("----- HOORAY!!!!")
                    self.hunter.time_frame = d[CM.BOT_STEP][CM.TIME_FRAME]

                elif CM.INIT in d:
                    self.hunter.start_new_game_run(d[CM.INIT])
                else:
                    raise KeyError
        except TimedOutExc:
            return

    def run(self):
        while True:
            logger.info('Hunter, start, time_frame=' + str(self.hunter.time_frame) + ', p=' + str(self.hunter.p))
            s = sched.scheduler(time.perf_counter, time.sleep)
            s.enter(0, 1, self.receivings_msgs)
            s.enter(TimesConf.TOTAL - 2 * TimesConf.BORDER_DELAY, 1, self.hunter.process_step)
            s.enter(TimesConf.TOTAL, 0, lambda *args: None)
            s.run()


class GameRun:
    def __init__(self, d_init):
        self.run_number = d_init[CM.RUN_NUMBER]
        self.cot_bot_name = d_init[CM.CAT_BOT_NAME]
        self.steps_number = d_init[CM.STEPS_NUMBER]
        self.field_size = d_init[CM.FIELD_SIZE]

        self.game_map = GameMap()
        self.game_map.teleports = d_init[CM.GAME_MAP][CM.TELEPORTS]


def main_client():
    ClientGame().run()


if __name__ == '__main__':
    main_client()
