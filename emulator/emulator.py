import os, pty, random, time
import fcntl
from multiprocessing import Process, Manager


def set_nonblocking(file_handle):
    """Make a file_handle non-blocking."""
    global OFLAGS
    OFLAGS = fcntl.fcntl(file_handle, fcntl.F_GETFL)
    nflags = OFLAGS | os.O_NONBLOCK
    fcntl.fcntl(file_handle, fcntl.F_SETFL, nflags)


manager_kill = Manager()
kill = manager_kill.Value('i', 0)


class EmulatorTDI:
    sv1 = b'\x00\x00\x00'
    sv1_range = b'\x00\x00\x00'
    sv2 = b'\x00\x00\x00'
    sv2_range = b'\x00\x00\x00'
    sv3 = b'\x00\x00\x00'
    sv3_range = b'\x00\x00\x00'
    tm = b'\x00\x00\x00'
    tm_range = b'\x00\x00\x00'
    sv2_double = b'\x00\x00\x00'
    sv2_double_range = b'\x00\x00\x00'

    def __init__(self):
        self.dummy_tdi_thread = Process(target=self.run_emulator)
        self.master, self.slave = pty.openpty()
        self.s_name = os.ttyname(self.slave)

    def init_work(self):
        set_nonblocking(self.master)
        self.dummy_tdi_thread.daemon = True
        self.dummy_tdi_thread.start()

    def run_emulator(self):

        while kill.value == 0:
            try:
                byte = os.read(self.master, 1)
                #print(byte)
                byte_list = [byte]
                while byte:
                    byte = os.read(self.master, 1)
                    byte_list.append(byte)

            except BlockingIOError:
                try:
                    if byte_list:
                        self.proces_info(byte_list)
                        byte_list = []
                except UnboundLocalError:
                    pass

    def proces_info(self, byte_list: list):
        i = 0
        print(byte_list)
        while i < len(byte_list):
            if byte_list[i] == b'\x14':
                os.write(self.master, b'\x88')
            if byte_list[i] == b'\xa2':
                self.sv1 = random.randint(32000, 128000)
                self.sv1_range = (self.sv1 + random.randint(32000, 48000)).to_bytes(3, 'big')
                self.sv1 = self.sv1.to_bytes(3, 'big')
                self.sv2 = random.randint(32000, 128000)
                self.sv2_range = (self.sv2 + random.randint(1280, 1920)).to_bytes(3, 'big')
                self.sv2 = self.sv2.to_bytes(3, 'big')
                self.sv3 = random.randint(32000, 128000).to_bytes(3, 'big')
                self.sv3_range = random.randint(32000, 48000).to_bytes(3, 'big')
                self.tm = random.randint(32000, 128000).to_bytes(3, 'big')
                self.tm_range = random.randint(32000, 48000).to_bytes(3, 'big')

                self.sv2_double = random.randint(32000, 128000)
                self.sv2_double_range = (self.sv2_double + random.randint(1280, 1920)).to_bytes(3, 'big')
                self.sv2_double = self.sv2_double.to_bytes(3, 'big')

                time.sleep(0.036)
                os.write(self.master, b'\xb1')

            if byte_list[i] == b'\xa3' and byte_list[i+1] == b'\x01':
                os.write(self.master, self.sv1)

            if byte_list[i] == b'\xa3' and byte_list[i+1] == b'\x02':
                os.write(self.master, self.sv1_range)

            if byte_list[i] == b'\xa3' and byte_list[i+1] == b'\x03':
                os.write(self.master, self.sv2)

            if byte_list[i] == b'\xa3' and byte_list[i+1] == b'\x04':
                os.write(self.master, self.sv2_range)

            if byte_list[i] == b'\xa3' and byte_list[i+1] == b'\x05':
                os.write(self.master, self.sv3)

            if byte_list[i] == b'\xa3' and byte_list[i+1] == b'\x06':
                os.write(self.master, self.sv3_range)

            if byte_list[i] == b'\xa3' and byte_list[i+1] == b'\x07':
                os.write(self.master, self.tm)

            if byte_list[i] == b'\xa3' and byte_list[i+1] == b'\x08':
                os.write(self.master, self.tm_range)

            if byte_list[i] == b'\xa3' and byte_list[i+1] == b'\x09':
                os.write(self.master, self.sv2_double)

            if byte_list[i] == b'\xa3' and byte_list[i+1] == b'\x0a':
                os.write(self.master, self.sv2_double_range)
            i += 1


class EmulatorZUP:
    volts = 0
    ampers = 0

    def __init__(self):
        self.dummy_zup_thread = Process(target=self.run_emulator)
        self.master, self.slave = pty.openpty()
        self.s_name = os.ttyname(self.slave)

    def init_work(self):
        set_nonblocking(self.master)
        self.dummy_zup_thread.daemon = True
        self.dummy_zup_thread.start()

    def run_emulator(self):

        while kill.value == 0:
            try:
                byte = os.read(self.master, 1)
                byte_list = [byte]
                while byte:
                    byte = os.read(self.master, 1)
                    byte_list.append(byte)

            except BlockingIOError:
                try:
                    if byte_list:
                        self.proces_info(byte_list)
                        byte_list = []
                except UnboundLocalError:
                    pass

    def proces_info(self, byte_list: list):
        i = 0
        print("байты в эмуляторе ЗУП", byte_list)
        if byte_list[1] == b'V':
            self.volts = byte_list[4].decode() + byte_list[5].decode() + byte_list[6].decode() + byte_list[7].decode() + byte_list[8].decode()
        if byte_list[1] == b'C':
            self.ampers = byte_list[4].decode() + byte_list[5].decode() + byte_list[6].decode() + byte_list[7].decode() + byte_list[8].decode()
        print(f"вольты {self.volts}  амперы {self.ampers}")
