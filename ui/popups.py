from kivy.uix.popup import Popup
from kivy.app import App


class DeviceConnectionError(Popup):
    auto_dismiss = False


class DeviceZupError(Popup):
    auto_dismiss = False


class RegistersMenu(Popup):
    auto_dismiss = False

    def read_regs(self):
        app = App.get_running_app()
        app.serialTDI.write(b'\xa3\x01')
        self.ids.rg1.text = "".join([hex(x)[2:].zfill(2).upper() for x in list(app.serialTDI.read(3))])
        app.serialTDI.write(b'\xa3\x02')
        self.ids.rg2.text = "".join([hex(x)[2:].zfill(2).upper() for x in list(app.serialTDI.read(3))])
        app.serialTDI.write(b'\xa3\x03')
        self.ids.rg3.text = "".join([hex(x)[2:].zfill(2).upper() for x in list(app.serialTDI.read(3))])
        app.serialTDI.write(b'\xa3\x04')
        self.ids.rg4.text = "".join([hex(x)[2:].zfill(2).upper() for x in list(app.serialTDI.read(3))])
        app.serialTDI.write(b'\xa3\x05')
        self.ids.rg5.text = "".join([hex(x)[2:].zfill(2).upper() for x in list(app.serialTDI.read(3))])
        app.serialTDI.write(b'\xa3\x06')
        self.ids.rg6.text = "".join([hex(x)[2:].zfill(2).upper() for x in list(app.serialTDI.read(3))])
        app.serialTDI.write(b'\xa3\x07')
        self.ids.rg7.text = "".join([hex(x)[2:].zfill(2).upper() for x in list(app.serialTDI.read(3))])
        app.serialTDI.write(b'\xa3\x08')
        self.ids.rg8.text = "".join([hex(x)[2:].zfill(2).upper() for x in list(app.serialTDI.read(3))])
        app.serialTDI.write(b'\xa3\x09')
        self.ids.rg9.text = "".join([hex(x)[2:].zfill(2).upper() for x in list(app.serialTDI.read(3))])
        app.serialTDI.write(b'\xa3\x0a')
        self.ids.rgA.text = "".join([hex(x)[2:].zfill(2).upper() for x in list(app.serialTDI.read(3))])


def open_registers_menu():
    pop = RegistersMenu()
    pop.open()
    pop.read_regs()
