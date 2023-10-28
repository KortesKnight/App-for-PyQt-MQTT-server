import windows._SubWindowClass as SubWindowClass


class ConfigWindow(SubWindowClass.SubWindow):

    def update_GUI(self):

        if self.need_to_update:
            if not self.device.compare_devices(self.copy_device):
                self.MAC_label.setText(self.device.device_MAC)
                self.location_label.setText(self.device.device_location)

                self.amount_electro_label.setText(str(self.device.device_power_count))
                self.amount_ultrasonic_label.setText(str(self.device.device_flow_count))
                self.amount_temp_label.setText(str(self.device.device_ds_count))
                self.amout_mech_label.setText(str(self.device.device_mech_flow_count))

                # Edit lines
                self.location_lineEdit.setText(self.device.device_location)
                self.amount_electro_lineEdit.setText(str(self.device.device_power_count))
                self.amount_ultrasonic_lineEdit.setText(str(self.device.device_flow_count))
                self.amount_temp_lineEdit.setText(str(self.device.device_ds_count))
                self.amout_mech_lineEdit.setText(str(self.device.device_mech_flow_count))

                self.copy_device.update_device_info(self.device)

            self.need_to_update = False

    def publish_new_data(self):

        if self.device.device_MAC is None:
            self.open_warning_window("No device has been selected!")
        else:
            device_loc = self.location_lineEdit.text()
            amount_electro = self.amount_electro_lineEdit.text()
            amount_flow_ultrasonic = self.amount_ultrasonic_lineEdit.text()
            amount_ds18b20 = self.amount_temp_lineEdit.text()
            amount_flow_mech = self.amout_mech_lineEdit.text()

            if amount_electro.isnumeric() and\
                    amount_flow_ultrasonic.isnumeric() and\
                    amount_ds18b20.isnumeric() and\
                    amount_flow_mech.isnumeric():

                message = f'SetConfig "{device_loc}" {amount_ds18b20} {amount_flow_ultrasonic} ' \
                          f'{amount_electro} {amount_flow_mech}'

                topic = f"PLSEN_VYCEP/{self.device.device_MAC}/commands"

                '''message = "SetConfig \"" + device_loc + "\" " + amount_ds18b20 + " " + amount_flow_ultrasonic + " " + \
                          amount_electro + " " + amount_flow_mech
                topic = "PLSEN_VYCEP/" + self.device.device_MAC + "/commands"'''

                print(f"Topic: {topic} Message: {message}")

                if self.can_publish:
                    self.controller.connection.client.publish(topic, message)
            else:
                self.open_warning_window("Values are wrong!")
