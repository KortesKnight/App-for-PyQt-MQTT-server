import windows._SubWindowClass as SubWindowClass
import windows.DeviceTableClass as DeviceTableClass
from PyQt5.QtCore import QMutexLocker


class RestartDeviceWindow(SubWindowClass.SubWindow):

    device_table = None

    def init_specific_window_options(self):

        self.device_table = DeviceTableClass.DeviceTable(self.selected_device_table)

        new_y = 40
        self.device_table.table.move(self.device_table.table.pos().x(), new_y)

    def update_GUI(self):

        if self.need_to_update:
            with QMutexLocker(self.mutex):
                self.device_table.setSortingEnabled(False)
                self.device_table.update_items(self.selected_device)
                self.device_table.setSortingEnabled(True)

                self.need_to_update = False

    def publish_new_data(self):

        if len(self.selected_device) == 0:
            self.open_warning_window("No devices have been selected!")
        else:
            for device in self.selected_device:

                topic = f"PLSEN_VYCEP/{device.device_MAC}/commands"

                # topic = "PLSEN_VYCEP/" + device.device_MAC + "/commands"
                print(f"topic: {topic}, message: Restart")

                if self.can_publish:
                    self.controller.connection.client.publish(topic, "Restart")
                    # self.server_connection.client.publish(topic, "Restart")
