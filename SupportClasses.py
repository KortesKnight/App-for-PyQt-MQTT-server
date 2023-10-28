import json


# Class to processing data from server
class Message:
    _CONST_AMOUNT_POWER_CH = 2
    _CONST_AMOUNT_VOLUME = 7
    _CONST_AMOUNT_VOLUME_MECH = 3
    _CONST_AMOUNT_TEMP = 14

    def __init__(self, message):

        received_message = message.payload.decode()

        topic_data = message.topic.split('/')

        self.topic = topic_data[2]
        self.device_MAC = topic_data[1]
        self.device_location = None

        # variables for saving data from 'data' topic
        self.device_sw_v = None
        self.device_power_ch = []           # [None for el in range(self._CONST_AMOUNT_POWER_CH)]
        self.device_volume = []             # [None for el in range(self._CONST_AMOUNT_VOLUME)]
        self.device_ambient_temp = None
        self.device_volume_mech = []        # [None for el in range(self._CONST_AMOUNT_VOLUME_MECH)]
        self.device_temp = []               # [None for el in range(self._CONST_AMOUNT_TEMP)]

        # variables for saving data from 'diagnostics' topic
        self.device_ds_count = None
        self.device_flow_count = None
        self.device_power_count = None
        self.device_mech_flow_count = None
        self.device_power_ch0_calib = None
        self.device_power_ch1_calib = None

        self.fill_info(received_message)

    def fill_info(self, msg):

        try:
            msg_js = json.loads(msg)

            if self.topic == "data":

                self.device_location = msg_js['device']['loc']

                self.device_sw_v = msg_js['device']['sw_v']

                self.device_power_ch = self.parse_data_msg(msg_js, 'power', 'value') \
                    if 'power' in msg_js else []

                self.device_volume = self.parse_data_msg(msg_js, 'volume', 'value') \
                    if 'volume' in msg_js else []

                self.device_ambient_temp = msg_js['ambient']['temp'][0]['value'] \
                    if 'ambient' in msg_js else []

                self.device_volume_mech = self.parse_data_msg(msg_js, 'volume_mech', 'value') \
                    if 'volume_mech' in msg_js else []

                self.device_temp = self.parse_data_msg(msg_js, 'temp', 'value') \
                    if 'temp' in msg_js else []

            elif self.topic == "diagnostics":
                self.device_ds_count = msg_js['ds_count']
                self.device_flow_count = msg_js['flow_count']
                self.device_power_count = msg_js['power_count']
                self.device_mech_flow_count = msg_js['mech_flow_count']
                self.device_power_ch0_calib = msg_js['power_ch0_calib']
                self.device_power_ch1_calib = msg_js['power_ch1_calib']
            else:
                print("WARNING: Unknown topic was received!")

        except json.JSONDecodeError as err:
            print(f"ERROR: Impossible to decode message \"{msg}\" to JSON file")
            print("ERROR: Error value is -", err)

    @staticmethod
    def parse_data_msg(msg_js, channel, value):

        ret = []

        for el in msg_js[channel]:
            ret.append(el[value])

        return ret


# Class to processing data and creating Device object
class Device:

    def __init__(self):
        self.device_location = None
        self.device_MAC = None

        # variables for saving data from 'data' topic
        self.device_sw_v = None
        self.device_power_ch = None
        self.device_volume = None
        self.device_temp_ambient = None
        self.device_volume_mech = None
        self.device_temp = None

        # variables for saving data from 'diagnostics' topic
        self.device_ds_count = None
        self.device_flow_count = None
        self.device_power_count = None
        self.device_mech_flow_count = None
        self.device_power_ch0_calib = None
        self.device_power_ch1_calib = None

    def update_device_info(self, device_info):

        general_attrs = ['device_location', 'device_MAC']
        data_topic_attrs = ['sw_v', 'power_ch', 'volume', 'temp_ambient', 'volume_mech', 'temp']
        diagnostics_topic_attrs = [
        'ds_count', 'flow_count', 'power_count', 'mech_flow_count', 'power_ch0_calib', 'power_ch1_calib']

        for attr in general_attrs:
            setattr(self, attr, getattr(device_info, attr))

        for attr in data_topic_attrs:
            test = getattr(device_info, f'device_{attr}')
            setattr(self, f'device_{attr}', getattr(device_info, f'device_{attr}'))

        for attr in diagnostics_topic_attrs:
            setattr(self, f'device_{attr}', getattr(device_info, f'device_{attr}'))

    def fill_info_msg(self, msg: Message):

        # General attributes
        general_attrs = ['device_MAC']

        # Data topic attributes
        data_topic_attrs = [
            'device_location', 'device_sw_v', 'device_power_ch',
            'device_volume', 'device_ambient_temp', 'device_volume_mech',
            'device_temp'
        ]

        # Diagnostics topic attributes
        diagnostics_topic_attrs = [
            'device_ds_count', 'device_flow_count', 'device_power_count',
            'device_mech_flow_count', 'device_power_ch0_calib', 'device_power_ch1_calib'
        ]

        # Setting general attributes
        for attr in general_attrs:
            setattr(self, attr, getattr(msg, attr))

        # Setting data topic attributes
        for attr in data_topic_attrs:
            setattr(self, attr, getattr(msg, attr))

        # Setting diagnostics topic attributes
        for attr in diagnostics_topic_attrs:
            setattr(self, attr, getattr(msg, attr))

    def update_data_topic(self, msg: Message):
        self.device_location = msg.device_location
        self.device_sw_v = msg.device_sw_v
        self.device_power_ch = msg.device_power_ch
        self.device_volume = msg.device_volume
        self.device_temp_ambient = msg.device_ambient_temp
        self.device_volume_mech = msg.device_volume_mech
        self.device_temp = msg.device_temp

    def update_diagnostics_topic(self, msg: Message):
        self.device_ds_count = msg.device_ds_count
        self.device_flow_count = msg.device_flow_count
        self.device_power_count = msg.device_power_count
        self.device_mech_flow_count = msg.device_mech_flow_count
        self.device_power_ch0_calib = msg.device_power_ch0_calib
        self.device_power_ch1_calib = msg.device_power_ch1_calib

    def compare_devices(self, other) -> bool:

        general_attrs = ['device_location', 'device_MAC']
        data_topic_attrs = ['sw_v', 'power_ch', 'volume', 'temp_ambient', 'volume_mech', 'temp']
        diagnostics_topic_attrs = [
            'ds_count', 'flow_count', 'power_count', 'mech_flow_count', 'power_ch0_calib', 'power_ch1_calib']

        for attr in general_attrs:
            if getattr(self, attr) != getattr(other, attr):
                return False

        for attr in data_topic_attrs:
            if getattr(self, f'device_{attr}') != getattr(other, f'device_{attr}'):
                return False

        for attr in diagnostics_topic_attrs:
            if getattr(self, f'device_{attr}') != getattr(other, f'device_{attr}'):
                return False

        return True

    def print_info(self):

        general_attrs = ['device_location', 'device_MAC']
        data_topic_attrs = ['sw_v', 'power_ch', 'volume', 'temp_ambient', 'volume_mech', 'temp']
        diagnostics_topic_attrs = [
            'ds_count', 'flow_count', 'power_count', 'mech_flow_count', 'power_ch0_calib', 'power_ch1_calib']

        general_info = ''
        data_topic = ''
        diagnostics_topic = ''

        for attr in general_attrs:
            general_info += f' {getattr(self, attr)}'

        for attr in data_topic_attrs:
            data_topic += f" {getattr(self, f'device_{attr}')}"

        for attr in diagnostics_topic_attrs:
            diagnostics_topic += f" {getattr(self, f'device_{attr}')}"

        print(f"Info device {general_info}: {data_topic}, {diagnostics_topic}")