from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.config import Config

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('kivy', 'exit_on_escape', 0)


class KIA_BI03(MDApp):
    def __init__(self, **kwargs):
        super(KIA_BI03, self).__init__(**kwargs)
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.accent_palette = 'Green'
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self.root)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)
        self.pressed_keys = set()

    def build(self):
        return Builder.load_file('ui/main_menu.kv')