import ServerConnection
import SupportClasses
from PyQt5.QtCore import QMutex, QMutexLocker, QTimer
from typing import Optional


class Controller:

    def __init__(self, mutex: QMutex):

        print(f"Info: Controller {self} was inited")

        self.main_window = None
        self.connection = None
        self.mutex = mutex

        self.device_list = {}

        self.searched_line = ''

    def update_list(self, msg: ServerConnection) -> None:

        try:

            received_message = SupportClasses.Message(msg)
            mac = received_message.device_MAC

            with QMutexLocker(self.mutex):
                if received_message.device_MAC not in self.device_list:
                    self.add_new_device(received_message)
                else:
                    self.update_device_list(received_message)

                if self.searched_line == '' or self.check_matches(self.device_list[mac]):
                    self.main_window.device_to_update.append(mac)
                    self.main_window.need_to_update = True

        except ValueError as err:
            print(f"ERROR: Something was wrong! Code: {err}")

    # Adding new device to device_list
    def add_new_device(self, msg: SupportClasses.Message) -> None:

        mac = msg.device_MAC
        new_device = SupportClasses.Device()
        new_device.fill_info_msg(msg)

        self.device_list[mac] = new_device

    # Update item in device_list
    def update_device_list(self, msg: SupportClasses.Message) -> None:

        if msg.topic == "data":
            self.device_list[msg.device_MAC].update_data_topic(msg)
        else:
            self.device_list[msg.device_MAC].update_diagnostics_topic(msg)

    # get device from device list by mac
    def get_device(self, mac: str) -> SupportClasses.Device:

        return self.device_list[mac]

    def get_searched_device_list(self, searched_line: str) -> list:

        result_list = []
        self.searched_line = searched_line

        if len(self.searched_line) == 0:
            for mac in self.device_list:
                result_list.append(mac)

        else:

            for mac in self.device_list:
                device = self.device_list[mac]

                if self.check_matches(device):
                    result_list.append(mac)

        return result_list

    def check_matches(self, device: SupportClasses.Device) -> bool:

        # equivalent to loc = device.device_location if device.device_location is None else str(device.device_location)
        loc = device.device_location or str(device.device_location)

        mac = device.device_MAC

        # equivalent to sw_v = device.device_sw_v if device.device_sw_v is None else str(device.device_sw_v)
        sw_v = device.device_sw_v or str(device.device_sw_v)

        return (
            mac in self.main_window.device_searched_selected or
            self.searched_line in loc or
            self.searched_line in mac or
            self.searched_line in sw_v
        )

    def connect(self):

        try:
            print("Info: Connection to the MQTT server has been initialised")
            self.connection.connect_to_mqtt()
        except ValueError as err:
            print(f"ERROR: Something was wrong with MQTT! Code: {err}")

    def disconnect(self):

        if self.connection is not None:
            try:
                self.connection.close_connection()
                print("Info: Disconnected from the MQTT server")
            except ValueError as err:
                print(f"ERROR: Something was wrong with MQTT! Code: {err}")
