import select
import sys
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.graphics.svg import Svg
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scatter import Scatter
from kivy.uix.widget import Widget
from helpers.CommonInterface import GAME_CONF
from helpers.SettingKeeper import SK
from helpers import CommonInterface as CM


class Stater:
    cat_p = None
    hunter_p = None
    cat_direction = None


class SvgWidget(Scatter):
    def __init__(self, filename, **kwargs):
        super(SvgWidget, self).__init__(**kwargs)
        with self.canvas:
            svg = Svg(filename)
        self.size = 15, 15


class NyanCell(BoxLayout):
    def __init__(self, nyan_pos):
        super().__init__()
        # self.width, self.height = SK.CELL_WIDTH, SK.CELL_HEIGHT
        self.cell_x, self.cell_y = nyan_pos

        self.orientation = 'vertical'
        self.status_label = Label(
            text='[size=12]' + 'cell x:' + str(self.cell_x) + ' y:' + str(self.cell_y) + '[/size]',
            markup=True, size_hint_y=1)

        self.add_widget(self.status_label)

        self.space = BoxLayout(size_hint_y=8, background_color=(0.5, 0.9, 0.1, 1))
        self.add_widget(self.space)

    def check_updates(self, stater):
        self.space.clear_widgets()
        if stater.hunter_p is not None and (self.cell_x, self.cell_y) == stater.hunter_p:
            self.space.add_widget(SvgWidget('helpers/images/arrow-up.svg'))
        if stater.cat_p is not None and (self.cell_x, self.cell_y) == stater.cat_p:
            self.space.add_widget(Label(background_normal='helpers/images/min_cat.png',
                                        size=(20, 20)))


class NyanGame(BoxLayout):
    fields = [[None for i in range(GAME_CONF.FIELD_SIZE)] for j in range(GAME_CONF.FIELD_SIZE)]
    status_time = 1
    input_query = [0]
    cur_direction = None
    stater = None

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

        with self.canvas.before:
            Color(1, 0, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)

        horizontal_layout.add_widget(
            Label(text='Nyan', size_hint_x=2))

        horizontal_layout.add_widget(field_layout)
        horizontal_layout.add_widget(Button(text='Actions', size_hint_x=3))
        horizontal_layout.add_widget(self.status_layout)
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

    def read_input_data(self, t):
        if not select.select([sys.stdin, ], [], [], 0.0)[0]:
            return

        s = input()
        # print(len(s))
        # i = (input())
        # self.input_query[0] = i

    def send_direction(self):
        print(self.cur_direction)


class NyanApp(App):
    stater = None

    def build(self):
        Window.size = SK.MINIMUM_WINDOW_SIZE
        game = NyanGame(stater=self.stater)
        Clock.schedule_interval(game.update, 1.0 / SK.FPS)
        Clock.schedule_interval(game.read_input_data, 1.0 / SK.FPS)
        return game


def graphics_main():
    st = Stater()
    st.cat_direction = CM.LEFT
    st.cat_p = 0, 0
    st.hunter_p = 1, 1
    app = NyanApp()
    app.stater = st
    app.run()


if __name__ == '__main__':
    graphics_main()
