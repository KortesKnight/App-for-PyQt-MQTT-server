import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QMutex
import windows._MainWindowClass as MainWindowClass
import ControllerClass
import ServerConnection
# import cProfile


def main():
    mutex = QMutex()

    app = QApplication(sys.argv)

    main_window = MainWindowClass.MainWindow(mutex, sys.argv)
    controller = ControllerClass.Controller(mutex)
    mqtt_connection = ServerConnection.MQTTConnection()

    # init controller
    main_window.controller = controller
    mqtt_connection.controller = controller

    controller.main_window = main_window
    controller.connection = mqtt_connection

    main_window.show()
    controller.connect()

    main_window.init_windows()

    app.exec()

    controller.disconnect()


if __name__ == '__main__':
    # cProfile.run("main()", sort="cumulative")
    main()
