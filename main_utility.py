from time import localtime, strftime
from pathlib import Path
from threading import Thread
from kivy.app import App
from zup.zup_work import voltage


def run_cycle() -> None:
    """основной цикл работы"""
    app = App.get_running_app()
    if app.root.ids.auto_selector.active:
        app.serialTDI.write(b'\xa1\xf0')
        app.serialTDI.write(b'\xa2\x00')
    else:
        app.serialTDI.write(b'\xa1\xf1')
        if app.root.ids.single_selector.active:
            app.serialTDI.write(b'\xa2\x00')
        else:
            app.serialTDI.write(b'\xa2\x01')

    ans = app.serialTDI.read(1)

    if ans == b'\xb1':
        app.serialTDI.write(b'\xa3\x01')
        sv1_start = app.serialTDI.read(3)
        app.serialTDI.write(b'\xa3\x02')
        sv1_range = app.serialTDI.read(3)
        app.serialTDI.write(b'\xa3\x03')
        sv2_start = app.serialTDI.read(3)
        app.serialTDI.write(b'\xa3\x04')
        sv2_range = app.serialTDI.read(3)
        app.serialTDI.write(b'\xa3\x05')
        sv3_start = app.serialTDI.read(3)
        app.serialTDI.write(b'\xa3\x06')
        sv3_range = app.serialTDI.read(3)
        app.serialTDI.write(b'\xa3\x07')
        tm_start = app.serialTDI.read(3)
        app.serialTDI.write(b'\xa3\x08')
        tm_range = app.serialTDI.read(3)

        if app.root.ids.double_selector.active:
            app.serialTDI.write(b'\xa3\x09')
            sv2_double_start = app.serialTDI.read(3)
            app.serialTDI.write(b'\xa3\x0a')
            sv2_double_range = app.serialTDI.read(3)
            app.root.ids.sv2_double_start.text = "{0:.2f}".format((int.from_bytes(sv2_double_start, 'big') * 62.25) / 1_000_000) + " мс"
            app.root.ids.sv2_double_range.text = "{0:.2f}".format(((
                                                                    int.from_bytes(sv2_double_range,
                                                                                   'big') * 62.25 - int.from_bytes(
                                                                sv2_double_start, 'big') * 62.25) / 1_000)) + " мкс"
        else:
            app.root.ids.sv2_double_start.text = "Н/Д"
            app.root.ids.sv2_double_range.text = "Н/Д"
            app.root.ids.sv2_double_start_norm.text = "Норма"
            app.root.ids.sv2_double_range_norm.text = "Норма"
            app.root.ids.sv2_double_start_norm.color = [1, 1, 1, 1]
            app.root.ids.sv2_double_range_norm.color = [1, 1, 1, 1]

        app.root.ids.sv1_start.text = "{0:.2f}".format((int.from_bytes(sv1_start, 'big') * 62.25) / 1_000_000) + " мс"
        app.root.ids.sv1_range.text = "{0:.2f}".format((((int.from_bytes(sv1_range, 'big')) * 62.25) - (int.from_bytes(sv1_start, 'big') * 62.25)) / 1_000_000) + " мс"
        app.root.ids.sv2_start.text = "{0:.2f}".format((int.from_bytes(sv2_start, 'big') * 62.25) / 1_000_000) + " мс"
        app.root.ids.sv2_range.text = "{0:.2f}".format(((
            int.from_bytes(sv2_range, 'big') * 62.25 - int.from_bytes(sv2_start, 'big') * 62.25) / 1_000)) + " мкс"

        app.root.ids.sv3_start.text = "{0:.2f}".format((int.from_bytes(sv3_start, 'big') * 62.25) / 1_000_000) + " мс"

        app.root.ids.sv3_range.text = "{0:.2f}".format((
            int.from_bytes(sv1_range, 'big') * 62.25 - int.from_bytes(sv3_range, 'big') * 62.25) / 1_000_000) + " мс"

        app.root.ids.tm_start.text = "{0:.2f}".format((int.from_bytes(tm_start, 'big') * 62.25) / 1_000_000) + " мс"
        app.root.ids.tm_range.text = "{0:.2f}".format((
                                                               int.from_bytes(sv1_range,
                                                                              'big') * 62.25 - int.from_bytes(tm_range,
                                                                                                              'big') * 62.25) / 1_000_000) + " мс"
        determine_norms()
        write_report_to_file()


def run_psi():
    app = App.get_running_app()
    Path("results_files").mkdir(exist_ok=True)
    app.result_file_name = 'results_files/' + strftime("%Y-%m-%d %H:%M", localtime()) + ".txt"
    app.run_process = Thread(target=run_n_cycles)
    app.run_process.daemon = True
    app.stop_psi = False
    app.run_process.start()
    app.root.ids.run.disabled = True


def run_n_cycles():
    app = App.get_running_app()

    for cycle in range(1, int(app.root.ids.cycle_number.text)+1):
        if app.root.ids.low_voltage.active:
            voltage(app.serial_ZUP, {1: [27.0, 0.5]})
        elif app.root.ids.norm_voltage.active:
            voltage(app.serial_ZUP, {1: [30.0, 0.5]})
        elif app.root.ids.high_voltage.active:
            voltage(app.serial_ZUP, {1: [33.0, 0.5]})
        else:
            if cycle % 3 == 0:
                voltage(app.serial_ZUP, {1: [30.0, 0.5]})
            elif cycle % 3 == 1:
                voltage(app.serial_ZUP, {1: [27.0, 0.5]})
            else:
                voltage(app.serial_ZUP, {1: [33.0, 0.5]})

        if not app.stop_psi:
            app.root.ids.current_cycle.text = str(cycle)
            run_cycle()

    app.root.ids.run.disabled = False


def determine_norms():
    """Высчитывание и отображение норма - не норма"""
    app = App.get_running_app()
    if app.root.ids.auto_selector.active:
        if 3 <= float(app.root.ids.sv1_start.text.split(" ")[0]) <= 6:
            app.root.ids.sv1_start_norm.text = "Норма"
            app.root.ids.sv1_start_norm.color = [0, 1, 0, 1]
        else:
            app.root.ids.sv1_start_norm.text = "Не Норма"
            app.root.ids.sv1_start_norm.color = [1, 0, 0, 1]

        if 2.25 <= float(app.root.ids.sv1_range.text.split(" ")[0]) <= 2.75:
            app.root.ids.sv1_range_norm.text = "Норма"
            app.root.ids.sv1_range_norm.color = [0, 1, 0, 1]
        else:
            app.root.ids.sv1_range_norm.text = "Не Норма"
            app.root.ids.sv1_range_norm.color = [1, 0, 0, 1]

        if 3 <= float(app.root.ids.sv2_start.text.split(" ")[0]) <= 6:
            app.root.ids.sv2_start_norm.text = "Норма"
            app.root.ids.sv2_start_norm.color = [0, 1, 0, 1]
        else:
            app.root.ids.sv2_start_norm.text = "Не Норма"
            app.root.ids.sv2_start_norm.color = [1, 0, 0, 1]
        if 90 <= float(app.root.ids.sv2_range.text.split(" ")[0]) <= 110:
            app.root.ids.sv2_range_norm.text = "Норма"
            app.root.ids.sv2_range_norm.color = [0, 1, 0, 1]
        else:
            app.root.ids.sv2_range_norm.text = "Не Норма"
            app.root.ids.sv2_range_norm.color = [1, 0, 0, 1]

        if 1.5 <= float(app.root.ids.sv3_start.text.split(" ")[0]) <= 7.5:
            app.root.ids.sv3_start_norm.text = "Норма"
            app.root.ids.sv3_start_norm.color = [0, 1, 0, 1]
        else:
            app.root.ids.sv3_start_norm.text = "Не Норма"
            app.root.ids.sv3_start_norm.color = [1, 0, 0, 1]

        if float(app.root.ids.sv3_range.text.split(" ")[0]) <= 2.3:
            app.root.ids.sv3_range_norm.text = "Норма"
            app.root.ids.sv3_range_norm.color = [0, 1, 0, 1]
        else:
            app.root.ids.sv3_range_norm.text = "Не Норма"
            app.root.ids.sv3_range_norm.color = [1, 0, 0, 1]

        if 1.5 <= float(app.root.ids.tm_start.text.split(" ")[0]) <= 7.5:
            app.root.ids.tm_start_norm.text = "Норма"
            app.root.ids.tm_start_norm.color = [0, 1, 0, 1]
        else:
            app.root.ids.tm_start_norm.text = "Не Норма"
            app.root.ids.tm_start_norm.color = [1, 0, 0, 1]

        if float(app.root.ids.tm_range.text.split(" ")[0]) <= 2.3:
            app.root.ids.tm_range_norm.text = "Норма"
            app.root.ids.tm_range_norm.color = [0, 1, 0, 1]
        else:
            app.root.ids.tm_range_norm.text = "Не Норма"
            app.root.ids.tm_range_norm.color = [1, 0, 0, 1]

    else:
        if 3.25 <= float(app.root.ids.sv1_start.text.split(" ")[0]) <= 6.25:
            app.root.ids.sv1_start_norm.text = "Норма"
            app.root.ids.sv1_start_norm.color = [0, 1, 0, 1]
        else:
            app.root.ids.sv1_start_norm.text = "Не Норма"
            app.root.ids.sv1_start_norm.color = [1, 0, 0, 1]

        if 2.25 <= float(app.root.ids.sv1_range.text.split(" ")[0]) <= 2.75:
            app.root.ids.sv1_range_norm.text = "Норма"
            app.root.ids.sv1_range_norm.color = [0, 1, 0, 1]
        else:
            app.root.ids.sv1_range_norm.text = "Не Норма"
            app.root.ids.sv1_range_norm.color = [1, 0, 0, 1]

        if 3.25 <= float(app.root.ids.sv2_start.text.split(" ")[0]) <= 6.25:
            app.root.ids.sv2_start_norm.text = "Норма"
            app.root.ids.sv2_start_norm.color = [0, 1, 0, 1]
        else:
            app.root.ids.sv2_start_norm.text = "Не Норма"
            app.root.ids.sv2_start_norm.color = [1, 0, 0, 1]
        if 90 <= float(app.root.ids.sv2_range.text.split(" ")[0]) <= 110:
            app.root.ids.sv2_range_norm.text = "Норма"
            app.root.ids.sv2_range_norm.color = [0, 1, 0, 1]
        else:
            app.root.ids.sv2_range_norm.text = "Не Норма"
            app.root.ids.sv2_range_norm.color = [1, 0, 0, 1]

        if 1.75 <= float(app.root.ids.sv3_start.text.split(" ")[0]) <= 7.75:
            app.root.ids.sv3_start_norm.text = "Норма"
            app.root.ids.sv3_start_norm.color = [0, 1, 0, 1]
        else:
            app.root.ids.sv3_start_norm.text = "Не Норма"
            app.root.ids.sv3_start_norm.color = [1, 0, 0, 1]

        if float(app.root.ids.sv3_range.text.split(" ")[0]) <= 2.3:
            app.root.ids.sv3_range_norm.text = "Норма"
            app.root.ids.sv3_range_norm.color = [0, 1, 0, 1]
        else:
            app.root.ids.sv3_range_norm.text = "Не Норма"
            app.root.ids.sv3_range_norm.color = [1, 0, 0, 1]

        if 1.75 <= float(app.root.ids.tm_start.text.split(" ")[0]) <= 7.75:
            app.root.ids.tm_start_norm.text = "Норма"
            app.root.ids.tm_start_norm.color = [0, 1, 0, 1]
        else:
            app.root.ids.tm_start_norm.text = "Не Норма"
            app.root.ids.tm_start_norm.color = [1, 0, 0, 1]

        if float(app.root.ids.tm_range.text.split(" ")[0]) <= 2.3:
            app.root.ids.tm_range_norm.text = "Норма"
            app.root.ids.tm_range_norm.color = [0, 1, 0, 1]
        else:
            app.root.ids.tm_range_norm.text = "Не Норма"
            app.root.ids.tm_range_norm.color = [1, 0, 0, 1]

        if app.root.ids.double_selector.active:
            if 90 <= float(app.root.ids.sv2_double_start.text.split(" ")[0]) - float(app.root.ids.sv2_start.text.split(" ")[0]) <= 110:
                app.root.ids.sv2_double_start_norm.text = "Норма"
                app.root.ids.sv2_double_start_norm.color = [0, 1, 0, 1]
            else:
                app.root.ids.sv2_double_start_norm.text = "Не Норма"
                app.root.ids.sv2_double_start_norm.color = [1, 0, 0, 1]

            if 90 <= float(app.root.ids.sv2_double_range.text.split(" ")[0]) <= 110:
                app.root.ids.sv2_double_range_norm.text = "Норма"
                app.root.ids.sv2_double_range_norm.color = [0, 1, 0, 1]
            else:
                app.root.ids.sv2_double_range_norm.text = "Не Норма"
                app.root.ids.sv2_double_range_norm.color = [1, 0, 0, 1]


def write_report_to_file():
    app = App.get_running_app()
    with open(app.result_file_name, "a+") as f:
        f.write(app.root.ids.current_cycle.text + " цикл" + '\n')

        if app.root.ids.low_voltage.active:
            f.write("Питание Пониженное" + '\n')
        elif app.root.ids.norm_voltage.active:
            f.write("Питание Номинал" + '\n')
        elif app.root.ids.high_voltage.active:
            f.write("Питание Повышенное" + '\n')
        else:
            if int(app.root.ids.current_cycle.text) % 3 == 0:
                f.write("Питание Номинал" + '\n')
            elif int(app.root.ids.current_cycle.text) % 3 == 1:
                f.write("Питание Пониженное" + '\n')
            else:
                f.write("Питание Повышенное" + '\n')

        f.write(f"СВ1 начало: {app.root.ids.sv1_start.text} {app.root.ids.sv1_start_norm.text}\n")
        f.write(f"СВ1 длит.: {app.root.ids.sv1_range.text} {app.root.ids.sv1_range_norm.text}\n")
        f.write(f"СВ2 начало: {app.root.ids.sv2_start.text} {app.root.ids.sv2_start_norm.text}\n")
        f.write(f"СВ2 длит.: {app.root.ids.sv2_range.text} {app.root.ids.sv2_range_norm.text}\n")
        f.write(f"СВ3 начало: {app.root.ids.sv3_start.text} {app.root.ids.sv3_start_norm.text}\n")
        f.write(f"СВ3 длит.: {app.root.ids.sv3_range.text} {app.root.ids.sv3_range_norm.text}\n")
        f.write(f"ТМ начало: {app.root.ids.tm_start.text} {app.root.ids.tm_start_norm.text}\n")
        f.write(f"ТМ длит.: {app.root.ids.tm_range.text} {app.root.ids.tm_range_norm.text}\n")
        if app.root.ids.double_selector.active:
            f.write(f"СВ2 2 начало: {app.root.ids.sv2_double_start.text} {app.root.ids.sv2_double_start_norm.text}\n")
            f.write(f"СВ2 2 длит.: {app.root.ids.sv2_double_range.text} {app.root.ids.sv2_double_range_norm.text}\n")
        f.write('\n')
