from PyQt5.QtWidgets import QMainWindow, QHeaderView, QCheckBox, QTableWidgetItem
from PyQt5.QtCore import QMutexLocker, QTimer, Qt
from PyQt5 import uic

import SupportClasses
import windows.ConfigWindowClass as ConfigWindowClass
import windows.SettingCalibDataWindowClass as SettingCalibDataWindowClass
import windows.RestartDeviceWindowClass as RestartDeviceWindowClass
import windows.OTAUpdateDeviceWindowClass as OTAUpdateDeviceWindowClass

import os
from typing import Union

ui_path_main = os.path.join(os.path.dirname(__file__), 'main.ui')
ui_path_config = os.path.join(os.path.dirname(__file__), 'configure.ui')
ui_path_callib = os.path.join(os.path.dirname(__file__), 'calibration.ui')
ui_path_restart = os.path.join(os.path.dirname(__file__), 'restart_device.ui')
ui_path_ota_manager = os.path.join(os.path.dirname(__file__), 'ota_ui.ui')


class MainWindow(QMainWindow):

    windows_classes_list = [ConfigWindowClass.ConfigWindow,
                            SettingCalibDataWindowClass.SettingCalibDataWindow,
                            RestartDeviceWindowClass.RestartDeviceWindow,
                            OTAUpdateDeviceWindowClass.OTAUpdateDeviceWindow]

    # windows_UI_list = ["configure.ui", "calibration.ui", "restart_device.ui", "ota_ui.ui"]
    windows_UI_list = [ui_path_config,
                       ui_path_callib,
                       ui_path_restart,
                       ui_path_ota_manager]
    windows_tittle_list = ["Configuration manager", "Calibration manager", "Restart manager", "OTA manager"]

    highlighted_device_MAC = ['', -1]

    selected_items_list = {}

    def __init__(self, mutex, publish_state):

        self.controller = None
        self.publish_state = True if len(publish_state) > 1 and publish_state[1] == "pub" else False

        # Server connection
        # There are variables to collect data from server
        self.device_to_update = []
        self.device_shown_dict = {}

        # Initialization main window
        # Inherit the properties of the main class
        super().__init__()
        # Load design window
        uic.loadUi(ui_path_main, self)

        self.init_table()

        # Initialization working environment
        # Init mutex for work with shared data
        self.mutex = mutex
        # It's list to collect all active windows
        self.window_list = None

        # Set signals in window
        # Set double click on table widget
        self.device_table.cellDoubleClicked.connect(self.cell_double_clicked)
        # Subscribe on Change events in device_table (device_table is name from Qt Designer)
        self.device_table.cellClicked.connect(self.handle_selection_change)
        # Set signals on buttons in windows
        self.all_btn.clicked.connect(self.select_all)
        self.clear_btn.clicked.connect(self.unselect_all)
        self.toggle_all_btn.clicked.connect(self.toggle_all)
        # Set signal on line edit field
        self.cur_dev_lineEdit.textChanged.connect(self.redraw_device_list)
        # There are variables to collect data and work with them with edit line
        self.line_edit_list = {}
        self.device_searched_selected = {}
        self.search_state = False
        self.need_to_update_highlighted_item = False

        # There are signals to open windows
        # set event on each button from interface of Main Window
        self.config_button.clicked.connect(lambda: self.open_window(0))
        self.set_calib_button.clicked.connect(lambda: self.open_window(1))
        self.restart_dev_button.clicked.connect(lambda: self.open_window(2))
        self.update_button.clicked.connect(lambda: self.open_window(3))

        # It's working with GUI
        self.need_to_update = False
        timer = QTimer(self, interval=50, timeout=self.update_GUI)
        timer.start()

        print(f"Info: Window {self.__class__.__name__} has been inited")
    # ------------------------------------------------------------------------------------------------------------------

    # Initialization working environment
    def init_windows(self):
        print(f"Info: Window{self.__class__.__name__} has inited {self.controller}")
        # windows = []
        self.window_list = []

        for cls, ui, title in zip(self.windows_classes_list, self.windows_UI_list, self.windows_tittle_list):
            new_win = cls(ui, title, self.mutex, self.controller, self.publish_state)
            # new_win = cls(ui, title, self.mutex, None)
            self.window_list.append(new_win)

        # return windows

    def init_table(self):

        # Set fixed size of main window
        self.setFixedSize(self.width(), self.height())
        self.device_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    # ------------------------------------------------------------------------------------------------------------------

    # Realization of signals with active buttons
    def cell_double_clicked(self, row, col):

        device_mac = self.device_table.item(row, 2).text()
        item = self.device_table.cellWidget(row, 0)

        device = self.controller.get_device(device_mac)

        if device not in self.selected_items_list:
            item.setCheckState(Qt.Checked)
        else:
            item.setCheckState(Qt.Unchecked)

    # def handle_selection_change(self, row, optional: int | SupportClasses.Device):
    def handle_selection_change(self, row, optional: Union[int, None]):

        if optional is None:
            highlighted_device = None
        else:
            highlighted_device = self.device_table.item(row, 2).text()

            if highlighted_device != self.highlighted_device_MAC[0]:
                self.highlighted_device_MAC[0], self.highlighted_device_MAC[1] = highlighted_device, row

        for win in self.window_list:
            if win is not None:
                if highlighted_device is None:
                    device = SupportClasses.Device()
                else:
                    device = self.controller.get_device(highlighted_device)
                win.update_device_info(device)

    def select_all(self):

        for row in range(self.device_table.rowCount()):
            item = self.device_table.cellWidget(row, 0)

            if item.checkState() == Qt.Unchecked:
                item.setCheckState(Qt.Checked)

    def unselect_all(self):

        for row in range(self.device_table.rowCount()):
            item = self.device_table.cellWidget(row, 0)

            if item.checkState() == Qt.Checked:
                item.setCheckState(Qt.Unchecked)

    def toggle_all(self):

        for row in range(self.device_table.rowCount()):
            item = self.device_table.cellWidget(row, 0)

            if item.checkState() == Qt.Checked:
                item.setCheckState(Qt.Unchecked)
            else:
                item.setCheckState(Qt.Checked)

    def redraw_device_list(self, searched_line):

        with QMutexLocker(self.mutex):

            searched_devices = self.controller.get_searched_device_list(searched_line)

            self.highlighted_device_MAC = ['', -1]
            self.need_to_update_highlighted_item = True
            self.device_shown_dict = {}
            self.device_searched_selected = {}

            self.device_table.setRowCount(0)

            for device in searched_devices:
                self.device_to_update.append(device)

            self.need_to_update = True

    # ------------------------------------------------------------------------------------------------------------------

    # Realization of signal with opening window by buttons
    def open_window(self, window):
        if window is not None:
            self.window_list[window].show()
    # ------------------------------------------------------------------------------------------------------------------

    # Work with GUI
    def update_GUI(self):

        if self.need_to_update:

            with QMutexLocker(self.mutex):
                for mac in self.device_to_update:

                    if mac not in self.device_shown_dict:
                        self.device_shown_dict[mac] = True
                        self.add_row(mac)
                    else:
                        self.update_row(mac)

                self.device_to_update = []
                self.need_to_update = False

        if self.need_to_update_highlighted_item:
            if self.highlighted_device_MAC[0] != '':
                self.handle_selection_change(self.highlighted_device_MAC[1], 0)
            else:
                self.handle_selection_change(self.highlighted_device_MAC[1], None)
            self.need_to_update_highlighted_item = False

    def add_row(self, mac):

        self.device_table.setSortingEnabled(False)

        row_position = self.device_table.rowCount()
        self.device_table.insertRow(row_position)

        checkbox = QCheckBox()

        device = self.controller.get_device(mac)

        if device not in self.selected_items_list:
            checkbox.setChecked(False)
        else:
            checkbox.setChecked(True)

        checkbox.stateChanged.connect(self.checkbox_state_changed)

        location = QTableWidgetItem(f"{str(device.device_location)}")
        mac_device = QTableWidgetItem(mac)
        firmware = QTableWidgetItem(f"{str(device.device_sw_v)}")

        self.device_table.setCellWidget(row_position, 0, checkbox)
        self.device_table.setItem(row_position, 1, location)
        self.device_table.setItem(row_position, 2, mac_device)
        self.device_table.setItem(row_position, 3, firmware)

        self.device_table.setSortingEnabled(True)

    def update_row(self, mac):

        device = self.controller.get_device(mac)

        location = QTableWidgetItem(f"{device.device_location}")
        mac_device = QTableWidgetItem(mac)
        firmware = QTableWidgetItem(f"{str(device.device_sw_v)}")

        self.device_table.setSortingEnabled(False)
        for row in range(self.device_table.rowCount()):

            if self.device_table.item(row, 2).text() == mac:

                if self.device_table.item(row, 1).text() == "None":
                    self.device_table.setItem(row, 1, location)
                    print(f"Update: Actual MAC: {mac}, New location: {location.text()}")

                if self.device_table.item(row, 2).text() == "None":
                    self.device_table.setItem(row, 2, mac_device)

                if self.device_table.item(row, 3).text() == "None":
                    self.device_table.setItem(row, 3, firmware)

                if self.highlighted_device_MAC[0] != '' and self.highlighted_device_MAC[0] == mac:
                    self.need_to_update_highlighted_item = True

        self.device_table.setSortingEnabled(True)
    # ------------------------------------------------------------------------------------------------------------------

    def checkbox_state_changed(self, state):

        checkbox = self.sender()  # Get a signal from check-box which it send
        if isinstance(checkbox, QCheckBox):
            row = self.device_table.indexAt(checkbox.pos()).row()
            col = self.device_table.indexAt(checkbox.pos()).column()

            mac_address = self.device_table.item(row, col + 2).text()

            device = self.controller.get_device(mac_address)

            if state == Qt.Checked:
                self.selected_items_list[device] = True
            else:
                del self.selected_items_list[device]

            self.window_list[2].update_selected_list(self.selected_items_list)
            self.window_list[3].update_selected_list(self.selected_items_list)

    def closeEvent(self, event):
        for window in self.window_list:
            if window is not None:
                window.close()
