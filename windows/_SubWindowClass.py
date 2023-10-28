from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QDialog
from PyQt5.QtCore import QTimer, QMutex, QMutexLocker
import SupportClasses
import ControllerClass


# Class to create a draft for next windows
class SubWindow(QMainWindow):

    def __init__(self, ui: str, tittle: str, mutex: QMutex, controller: ControllerClass, publish_state):

        super().__init__()

        uic.loadUi(ui, self)

        self.setWindowTitle(tittle)

        self.setFixedSize(self.width(), self.height())

        self.confirm_button.clicked.connect(self.publish_new_data)
        self.cancel_button.clicked.connect(self.closeEvent)

        self.device = SupportClasses.Device()
        self.copy_device = SupportClasses.Device()
        self.need_to_update = True
        timer = QTimer(self, interval=50, timeout=self.update_GUI)
        timer.start()

        self.init_specific_window_options()

        self.mutex = mutex
        self.controller = controller

        self.device_list = {}
        self.selected_device = {}

        self.can_publish = publish_state

        print(f"Info from {self.__class__.__name__}: Window {self.__class__.__name__} has been inited")
        print(f"Info from {self.__class__.__name__}: Window{self.__class__.__name__} has inited {self.controller}")
        if self.can_publish:
            print(f"Info from {self.__class__.__name__}: publishing is allowed!")

    def init_specific_window_options(self):
        pass

    def update_device_info(self, device_info: SupportClasses.Device):

        with QMutexLocker(self.mutex):
            self.device.update_device_info(device_info)
            self.need_to_update = True

    def update_GUI(self):

        if self.need_to_update:
            print(f"INFO: {self} send GUI was updated")

    def update_selected_list(self, new_selected_device: SupportClasses.Device):

        with QMutexLocker(self.mutex):
            self.selected_device = new_selected_device

        self.need_to_update = True

    @staticmethod
    def open_warning_window(text: str):

        msg_box = QMessageBox()
        # msg_box.setIcon(QtWidgets.QMessageBox.Critical)
        msg_box.setIcon(QMessageBox.Information)

        msg_box.setText(text)
        msg_box.setWindowTitle("Check yourself!")

        msg_box.setStandardButtons(QMessageBox.Ok)

        msg_box.exec()

    def publish_new_data(self):
        print("INFO: Data was published!")

    @staticmethod
    def is_float(text: str) -> bool:

        try:
            float(text)
            return True
        except ValueError:
            return False

    def closeEvent(self, event):
        self.close()
