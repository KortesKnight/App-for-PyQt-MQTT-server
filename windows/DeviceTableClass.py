from PyQt5.QtWidgets import QTableWidget, QHeaderView, QTableWidgetItem


# Class to create a draft for table to processing data from server to GUI
class DeviceTable(QTableWidget):

    def __init__(self, working_table):

        super().__init__()

        self.table = working_table

        self.selected_list = []
        self.shown_items = {}

        self.table.setGeometry(20, 20, 530, 230)

        self.column_headers = ["Location", "MAC", "Firmware"]

        self.table.setHorizontalHeaderLabels(self.column_headers)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

        self.table.setSortingEnabled(True)

    def add_row(self):

        row_position = self.rowCount()
        self.table.insertRow(row_position)

    def clean_up_table(self):

        self.shown_items = {}
        for row in range(self.table.rowCount() - 1, -1, -1):
            self.table.removeRow(row)

    def update_items(self, selected_list):

        self.clean_up_table()

        for device in selected_list:
            row_pos = 0
            self.add_row()

            if device.device_MAC not in self.shown_items:
                self.shown_items[device.device_MAC] = True

                location = QTableWidgetItem(f"{device.device_location}")
                mac_device = QTableWidgetItem(device.device_MAC)
                firmware = QTableWidgetItem(f"{str(device.device_sw_v)}")

                self.table.setItem(row_pos, 0, location)
                self.table.setItem(row_pos, 1, mac_device)
                self.table.setItem(row_pos, 2, firmware)
