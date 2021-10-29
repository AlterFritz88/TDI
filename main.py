import os, sys
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.config import Config
from utils import get_connection

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('kivy', 'exit_on_escape', 0)


def resource_path():
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS)
    return os.path.join(os.path.abspath("."))


class TDI(MDApp):
    stop_psi = False

    def __init__(self, **kwargs):
        super(TDI, self).__init__(**kwargs)
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.accent_palette = 'Green'
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self.root)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)
        self.pressed_keys = set()

    def build(self):
        return Builder.load_file('ui/main_menu.kv')

    def on_start(self):
        get_connection()

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        # self._keyboard = None

    def _open_keyboard(self):
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _on_keyboard_up(self, keyboard, keycode):
        try:
            self.pressed_keys.remove(keycode[1])
        except:
            self.pressed_keys = set()

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        self.pressed_keys.add(keycode[1])


if __name__ == "__main__":
    from kivy.resources import resource_add_path, resource_find
    resource_add_path(os.path.join(resource_path()))
    Window.size = (1920, 1080)
    TDI().run()
