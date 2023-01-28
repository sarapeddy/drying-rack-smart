import json
import time

import serial
import serial.tools.list_ports
import configparser


class Bridge:
    def __init__(self):
        self.port_name = None
        self.ser = None
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.setupSerial()
        self.new_state = 0
        self.current_state = 0

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
                "is_raining": int(data[4])
            }
            return json_data
        if len(data) == 1:
            return {"state": int(data[0])}
        return json_data

    def check_rain(self, rain):
        if rain < 500:
            return True
        return False

    def check_weight(self, weight):
        return False

    def start_or_finish_drying_cycle(self, current_state, new_state):
        try:
            if current_state != new_state:
                if new_state:
                    buffer = 'start'
                else:
                    buffer = 'finish'

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
                    # json_data, self.new_state = self.loads_data()
                    json_data = self.loads_data()

                    try:
                        self.new_state = json_data["state"]
                    except KeyError:
                        if json_data != {}:
                            if self.check_rain(json_data["is_raining"]):
                                print("Send message to near drying rack")
                            if self.check_weight(json_data["cloth_weight"]):
                                #INSERT HERE A WRITE ON SERIAL PORT TO STOP THE CYCLE
                                print("Terminate Drying Cycle")

                #write on serial port
                self.current_state = self.start_or_finish_drying_cycle(self.current_state, self.new_state)


if __name__ == '__main__':
    br = Bridge()
    br.loop()
