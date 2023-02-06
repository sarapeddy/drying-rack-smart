import json
import time
import serial
import serial.tools.list_ports
from configparser import ConfigParser
import requests


class Bridge:
    """
        This class is the bridge between Arduino and Flask for Drying Rack Smart Iot Project
    """
    def __init__(self):
        self.port_name = None
        self.ser = None
        self.user = None
        self.cycle_id = None
        self.last_force_feed = None
        self.config = ConfigParser()
        self.config.read('config.ini')
        self.check_credentials()
        self.setupSerial()
        self.new_state = 0
        self.current_state = 0

    def check_credentials(self):
        while True:
            self.user = {
                'username': input("Insert username: "),
                'password': input("Insert password: ")
            }

            r = requests.post(url=f"http://{self.config.get('Api', 'host')}:5000/credentials", json=self.user)
            if r.text == "Login":
                break

    def setupSerial(self):
        if self.config.get("Serial", "UseDescription", fallback=False):
            self.port_name = self.config.get("Serial", "PortName", fallback="COM1")
        else:
            print("list of available ports: ")
            ports = serial.tools.list_ports.comports()

            for port in ports:
                print(port.device)
                print(port.description)
                if self.config.get("Serial", "PortDescription", fallback="arduino").lower() \
                        in port.description.lower():
                    self.port_name = port.device

        try:
            if self.port_name is not None:
                print("connecting to " + self.port_name)
                self.ser = serial.Serial(self.port_name, 9600, timeout=1)
        except:
            self.ser = None
            print("Connection failed")
            exit()

    def loads_data(self):
        data = str(self.ser.readline()).strip("\\n\\rb'").split(' ')
        json_data = {}
        if len(data) == 5:
            json_data = {
                "air_humidity": float(data[0]),
                "air_temperature": float(data[1]),
                "cloth_humidity": float(data[2]),
                "cloth_weight": int(data[3]),
                "is_raining": int(data[4]),
                "cycle_id": self.cycle_id
            }
            return json_data
        if len(data) == 1:
            return {"state": int(data[0])}
        return json_data

    def check_weight(self, weight):
        if self.last_force_feed is not None:
            if weight < 50 and self.last_force_feed < 50:
                r = requests.get(url=f"http://{self.config.get('Api', 'host')}:5000/{self.cycle_id}/inactive")
                self.last_force_feed = None
                self.cycle_id = None
                self.current_state = 0
                self.new_state = 0
                return True
        self.last_force_feed = weight
        return False

    def start_or_finish_drying_cycle(self, current_state, new_state):
        try:
            if current_state != new_state:
                if new_state:
                    buffer = 'start'
                    r = requests.post(url=f"http://{self.config.get('Api', 'host')}:5000/drying-cycle",
                                      json={'user': self.user['username']})
                    self.cycle_id = int(r.text)
                else:
                    buffer = 'finish'
                    r = requests.get(url=f"http://{self.config.get('Api', 'host')}:5000/{self.cycle_id}/inactive")
                    self.cycle_id = None

                self.ser.write(buffer.encode(encoding='ascii', errors='strict'))
                time.sleep(0.5)
                return new_state
            return current_state
        except serial.SerialException:
            print("Write on serial port failed")
            self.ser.close()
            self.ser = serial.Serial(self.port_name, 9600, timeout=1)

    def loop(self):
        # infinite loop for serial managing
        while True:
            if not self.ser is None:
                # look for a line from serial
                if self.ser.in_waiting > 0:
                    json_data = self.loads_data()

                    try:
                        self.new_state = json_data["state"]
                    except KeyError:
                        if json_data != {} and self.current_state == 1:
                            r = requests.post(url=f"http://{self.config.get('Api', 'host')}:5000/sensors/data", json=json_data)
                            if self.check_weight(int(json_data["cloth_weight"])):
                                buffer = 'force-finish'
                                self.ser.write(buffer.encode(encoding='ascii', errors='strict'))

                #write on serial port
                self.current_state = self.start_or_finish_drying_cycle(self.current_state, self.new_state)


if __name__ == '__main__':
    br = Bridge()
    br.loop()
