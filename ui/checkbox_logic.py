from kivy.app import App


def unblock_double() -> None:
    """Разблокирует динарный/двойной СВ"""

    app = App.get_running_app()
    if app.root.ids.common_selector.active:
        app.root.ids.common_test.disabled = False


def block_double() -> None:
    """Блокирует динарный/двойной СВ"""

    app = App.get_running_app()
    if app.root.ids.auto_selector.active:
        app.root.ids.common_test.disabled = True
