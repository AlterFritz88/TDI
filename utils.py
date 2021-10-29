import time
import serial
from kivy.app import App
from zup.zup_work import MODELL
from ui.popups import DeviceConnectionError, DeviceZupError
from emulator.emulator import EmulatorTDI, EmulatorZUP


def get_connection():
    possible_ports = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    app = App.get_running_app()
    port_real = None
    
    for port in possible_ports:
        try:
            ser = serial.Serial('/dev/ttyUSB{}'.format(port), baudrate=1000000, timeout=0.1)
            ser.write(b'\x14')
            ans = ser.read(1)

            if ans == b'\x88':
                app.serial = ser
                port_real = port
                print("Блок нашелся")
                break
            else:
                ans = ser.read_all()
                ser.reset_input_buffer()
                ser.reset_output_buffer()
                time.sleep(0.2)
        except (serial.serialutil.SerialException, BrokenPipeError) as e:
            print(str(e))
            continue

    if port_real:
        app.serialTDI = serial.Serial('/dev/ttyUSB{}'.format(port_real), baudrate=1000000, timeout=0.1)
    else:
        pop = DeviceConnectionError()
        pop.open()

    zup_port = None
    for port in possible_ports:
        if MODELL('/dev/ttyUSB{}'.format(port)):
            uart_ZUP = '/dev/ttyUSB{}'.format(port)
            print("ЗУП Нашелся!")
            zup_port = port
            break
    else:
        pop = DeviceZupError()
        pop.open()


def run_device_emulator():
    app = App.get_running_app()
    app.emulator_tdi = EmulatorTDI()
    app.emulator_tdi.init_work()
    uart_TDI = app.emulator_tdi.s_name
    app.serialTDI = serial.Serial(uart_TDI, baudrate=1000000, timeout=0.1)


def run_zup_emulator():
    app = App.get_running_app()
    app.emulator_zup = EmulatorZUP()
    app.emulator_zup.init_work()
    uart_ZUP = app.emulator_zup.s_name
    app.serial_ZUP = serial.Serial(uart_ZUP, baudrate=9600, timeout=0.01)
