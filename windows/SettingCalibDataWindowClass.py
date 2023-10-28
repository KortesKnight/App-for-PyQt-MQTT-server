import windows._SubWindowClass as SubWindowClass


class SettingCalibDataWindow(SubWindowClass.SubWindow):

    def update_GUI(self):

        if self.need_to_update:
            if not self.device.compare_devices(self.copy_device):
                self.MAC_label.setText(self.device.device_MAC)
                self.location_label.setText(self.device.device_location)
                self.calib_socket_1_label.setText(str(self.device.device_power_ch0_calib))
                self.calib_socket_2_label.setText(str(self.device.device_power_ch1_calib))

                # Edit lines
                self.calib_socket_1_lineEdit.setText(str(self.device.device_power_ch0_calib))
                self.calib_socket_2_lineEdit.setText(str(self.device.device_power_ch1_calib))

                self.copy_device.update_device_info(self.device)

            self.need_to_update = False

    def publish_new_data(self):

        if self.device.device_MAC is None:
            self.open_warning_window("No device has been selected!")
        else:
            calib1 = self.calib_socket_1_lineEdit.text()
            calib2 = self.calib_socket_2_lineEdit.text()

            if self.is_float(calib1) and self.is_float(calib2):
                message = f"SetCalib 1.0 {calib1} {calib2}"

                topic = f"PLSEN_VYCEP/{self.device.device_MAC}/commands"

                print(f"Topic: {topic} message: {message}")

                if self.can_publish:
                    self.controller.connection.client.publish(topic, message)
            else:
                self.open_warning_window("Values are wrong!")
