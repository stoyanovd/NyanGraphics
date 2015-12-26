import json
import os
import select
import sys
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.graphics.svg import Svg
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scatter import Scatter
from helpers import CommonInterface as CM
from helpers.CommonInterface import GAME_CONF
from helpers.SettingKeeper import SK, Stater
from helpers.TimeoutDecorator import timeout, TimedOutExc
from helpers.TimesConf import TimesConf


class SvgWidget(Scatter):
    def __init__(self, filename, **kwargs):
        super(SvgWidget, self).__init__(**kwargs)
        with self.canvas:
            svg = Svg(filename)
        self.size = 15, 15


class NyanArrow(Image):
    angle = NumericProperty(0)

    def __init__(self, nyan_angle, **kwargs):
        super().__init__(**kwargs)
        self.angle = int(nyan_angle)


class NyanCell(BoxLayout):
    def __init__(self, nyan_pos):
        super().__init__()
        # self.width, self.height = SK.CELL_WIDTH, SK.CELL_HEIGHT
        self.angle = 0
        self.cell_x, self.cell_y = nyan_pos

        self.orientation = 'vertical'
        self.status_label = Label(
            text='[size=12]' + 'cell x:' + str(self.cell_x) + ' y:' + str(self.cell_y) + '[/size]',
            markup=True, size_hint_y=1)

        # self.add_widget(self.status_label)

        self.space = BoxLayout(size_hint_y=8, background_normal='', background_color=(0.5, 0.9, 0.1, 1))
        self.add_widget(self.space)

    def check_updates(self, stater):
        # with self.canvas.before:
        #     Color(0, 0, 0)
        #     br = 1
        #     self.rect = Rectangle(x=self.x + br, y=self.y + br, width=self.width - 2 * br,
        #                           height=self.height - 2 * br)

        self.space.clear_widgets()
        if stater.hunter_p is not None and self.cell_x == stater.hunter_p[0] and self.cell_y == stater.hunter_p[1]:
            if stater.cat_direction in [CM.RIGHT, CM.UP, CM.LEFT, CM.DOWN]:
                angle = 90 * [CM.RIGHT, CM.UP, CM.LEFT, CM.DOWN].index(stater.cat_direction)
                self.space.add_widget(NyanArrow(nyan_angle=angle, source='helpers/images/arrow.png'))
            self.space.add_widget(Label(text=stater.cat_direction))

        if stater.cat_p is not None and self.cell_x == stater.cat_p[0] and self.cell_y == stater.cat_p[1]:
            self.space.add_widget(Image(source='helpers/images/min_cat.png'))
            # self.space.add_widget(Label(text=CM.CAT))


class NyanGame(BoxLayout):
    fields = [[None for i in range(GAME_CONF.FIELD_SIZE)] for j in range(GAME_CONF.FIELD_SIZE)]
    status_time = 1
    input_query = [0]
    cur_direction = None
    stater = None
    pipe_path = ""

    def get_status_string(self):
        return ['Time', '_____', 'frame №', '{0:7d}'.format(self.status_time),
                '_________________', 'second №', '{0:8.2f}'.format(self.status_time / SK.FPS),
                ' | ' + str(self.input_query) + ' |', 'cur_dir: ' + str(self.cur_direction)]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stater = kwargs['stater']
        self.status_layout = BoxLayout(orientation='vertical', size_hint_x=2)
        self.update_status()
        self.serve_fields()
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
        if self._keyboard.widget:
            # If it exists, this widget is a VKeyboard object which you can use
            # to change the keyboard layout.
            pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.pipe_path = kwargs['pipe_path']

    def update_status(self):
        res = self.get_status_string()
        self.status_layout = BoxLayout(orientation='vertical', size_hint_x=2)
        for line in res:
            self.status_layout.add_widget(Label(text=line))

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        word = keycode[1].upper()
        if word == 'T':
            word = 'TELEPORT'
        if word in ['UP', 'DOWN', 'LEFT', 'RIGHT', 'TELEPORT']:
            self.cur_direction = word
            self.send_direction()
        return True

    def serve_fields(self):
        field_layout = GridLayout(cols=GAME_CONF.FIELD_SIZE, rows=GAME_CONF.FIELD_SIZE,
                                  size_hint_x=20)

        for i in range(GAME_CONF.FIELD_SIZE):
            for j in range(GAME_CONF.FIELD_SIZE):
                self.fields[i][j] = NyanCell(nyan_pos=(i, j))
                field_layout.add_widget(self.fields[i][j])

        self.width, self.height = Window.size
        horizontal_layout = BoxLayout(orientation='horizontal')
        # horizontal_layout.width, horizontal_layout.height = Window.size

        # with self.canvas.before:
        #     Color(1, 0, 1)
        #     self.rect = Rectangle(size=self.size, pos=self.pos)

        # horizontal_layout.add_widget(Label(text='Nyan', size_hint_x=2))

        horizontal_layout.add_widget(field_layout)
        # horizontal_layout.add_widget(Button(text='Actions', size_hint_x=3))
        # horizontal_layout.add_widget(self.status_layout)
        self.add_widget(horizontal_layout)
        print('self:', self.x, self.y, self.width, self.height)
        print('vert:', horizontal_layout.x, horizontal_layout.y, horizontal_layout.width, horizontal_layout.height)
        print('grid:', field_layout.x, field_layout.y, field_layout.width, field_layout.height)
        cell = self.fields[0][0]
        print('cell:', cell.x, cell.y, cell.width, cell.height)
        cell = self.fields[2][2]
        print('cell:', cell.x, cell.y, cell.width, cell.height)

    def update(self, t):
        self.status_time += 1
        self.update_status()
        for i in range(GAME_CONF.FIELD_SIZE):
            for j in range(GAME_CONF.FIELD_SIZE):
                self.fields[i][j].check_updates(self.stater)

    @timeout(TimesConf.BORDER_DELAY)
    def read_input_data(self, t):
        try:
            if not os.path.exists(self.pipe_path):
                open(self.pipe_path, 'w+').close()

            with open(self.pipe_path, 'r') as f:
                try:
                    d = json.load(f)
                except:
                    return
            if d is None or not isinstance(d, dict):
                return
            if 'cat_direction' in d:
                self.stater.cat_direction = d['cat_direction']
            if 'cat_p' in d:
                self.stater.cat_p = d['cat_p']
            if 'hunter_p' in d:
                self.stater.hunter_p = d['hunter_p']

        except TimedOutExc:
            return

    def send_direction(self):
        print(self.cur_direction)


class NyanApp(App):
    stater = None
    pipe_path = ""

    def build(self):
        Window.size = SK.MINIMUM_WINDOW_SIZE
        game = NyanGame(stater=self.stater, pipe_path=self.pipe_path)
        Clock.schedule_interval(game.update, 1.0 / SK.FPS)
        Clock.schedule_interval(game.read_input_data, 1.0 / SK.FPS)
        return game


def createNyanApp(st, pipe_path):
    app = NyanApp()
    app.stater = st
    print('pipe file to connect:', pipe_path)
    assert pipe_path in [SK.TO_CLIENT_VIS_FIFO, SK.TO_SERVER_VIS_FIFO]
    app.pipe_path = pipe_path
    app.run()


def graphics_main(pipe_name):
    pipe_path = None
    try:
        if 'c' == pipe_name[0]:
            pipe_path = SK.TO_CLIENT_VIS_FIFO
        elif 's' == pipe_name[0]:
            pipe_path = SK.TO_SERVER_VIS_FIFO
        else:
            raise AssertionError
    except:
        print('Usage:')
        print('for server: python3 nyan_graphics.py s')
        print('for client: python3 nyan_graphics.py c')
        exit(1)
    st = Stater()
    st.cat_direction = CM.LEFT
    st.cat_p = 0, 0
    st.hunter_p = 1, 1
    createNyanApp(st, pipe_path)


if __name__ == '__main__':
    graphics_main(sys.argv[1])
