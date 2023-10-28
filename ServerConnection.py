import paho.mqtt.client as mqtt


class MQTTConnection:

    def __init__(self):
        self.TOPIC = "PLSEN_VYCEP/#"
        self.IP = 'mqtt.iobebo.testbed40.cz'
        self.login = "rabbitmqadmin"
        self.password = "qPe6Rr729fDse-"
        self.controller = None
        self.client = mqtt.Client("Statistics_monitor_plsen")

    def connect_to_mqtt(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set(self.login, self.password)
        self.client.connect(self.IP, 1883)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print(f"Info: Connected with result code {rc}")
        self.client.subscribe(self.TOPIC)

    def on_message(self, client, userdata, msg):
        self.controller.update_list(msg)

    def close_connection(self):
        self.client.disconnect()


