import windows._SubWindowClass as SubWindowClass
import windows.DeviceTableClass as DeviceTableClass
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtCore import QMutexLocker

from requests.auth import HTTPBasicAuth
import requests
import shutil
import zlib

import re
import asyncio
import aiohttp


class OTAUpdateDeviceWindow(SubWindowClass.SubWindow):

    highlighted_firmware = None

    firmwares_need_to_update = True
    ota_firmwares = []

    # firmware = None
    user = "ota_iobebo"
    password = "nQ6Hw5g43-skW+"

    device_table = None

    def init_specific_window_options(self):

        self.firmwares_list.itemSelectionChanged.connect(self.handle_selection_change)
        self.refresh_firmware_list()

        self.device_table = DeviceTableClass.DeviceTable(self.selected_device_table)

    def update_GUI(self):

        if self.need_to_update:
            with QMutexLocker(self.mutex):
                self.device_table.setSortingEnabled(False)
                self.device_table.update_items(self.selected_device)
                self.device_table.setSortingEnabled(True)

                self.need_to_update = False

        if self.firmwares_need_to_update:

            for firm in self.ota_firmwares:
                text = firm
                item = QListWidgetItem(text)

                self.firmwares_list.addItem(item)

            self.firmwares_need_to_update = False

    def get_ota_firmwares(self):
        ota_firmwares_list = []

        user = 'ota_iobebo'
        password = "nQ6Hw5g43-skW+"
        url = "http://ota.iobebo.testbed40.cz/ota/"
        res = requests.get(url, auth=HTTPBasicAuth(user, password))

        for line in res.text.split("\n"):
            line_out = str(re.findall(r"<a href=\"(.*?)\">", line)).replace("[\'", "").replace("\']", "")
            if len(line_out) > 3:
                ota_firmwares_list.append(line_out)

        self.ota_firmwares = ota_firmwares_list

    @staticmethod
    def crc(file_name):
        prev = 0
        for eachLine in open(file_name, "rb"):
            prev = zlib.crc32(eachLine, prev)
        return "%X" % (prev & 0xFFFFFFFF)


    def publish_new_data(self):

        firmware = self.highlighted_firmware

        if len(self.selected_device) == 0:
            self.open_warning_window("No device has been selected!")
        elif self.firmware is None:
            self.open_warning_window("No firmware has been selected!")
        else:

            print("Info: processing a request to the http://ota.iobebo.testbed40.cz/ota/  ...")
            resp = requests.get("http://ota.iobebo.testbed40.cz/ota/" + firmware, auth=(self.user, self.password),
                               stream=True)
            print("Info: request has been gotten!")

            with open('tmp.bin', 'wb') as out_file:
                shutil.copyfileobj(resp.raw, out_file)

            print("Info: bin has been written")

            crc = self.crc("tmp.bin")

            print("Info: start publishing:")
            for device in self.selected_device:

                message = f'OTA_Update "ota.iobebo.testbed40.cz" "/ota/{firmware}" ' \
                          f'"{self.user}" "{self.password}" "{crc.lower()}"'

                topic = f"PLSEN_VYCEP/{device.device_MAC}/commands"

                # message = "OTA_Update \"ota.iobebo.testbed40.cz\" \"/ota/" + firmware + "\"" + " \"" + self.user +\
                #          "\"" + " \"" + self.password + "\"" + " \"" + crc.lower() + "\""
                # topic = "PLSEN_VYCEP/" + device.device_MAC + "/commands"

                print(f"Topic: {topic} Message: {message}")

                if self.can_publish:
                    self.controller.connection.client.publish(topic, message)

    def handle_selection_change(self):
        selected_firmware = self.firmwares_list.selectedItems()[0]

        self.highlighted_firmware = selected_firmware.text()

    def refresh_firmware_list(self):

        self.firmwares_list.clear()
        self.get_ota_firmwares()
        self.firmwares_need_to_update = True

