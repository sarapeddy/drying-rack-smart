import serial
import serial.tools.list_ports
import configparser
from datetime import datetime


class Bridge():

    def __init__(self):
        self.buffer = []
        self.port_name = None
        self.ser = None
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.setupSerial()

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

    def loop(self):
        # infinite loop for serial managing
        while True:
            # look for a line from serial
            if not self.ser is None:
                if self.ser.in_waiting > 0:
                    data = str(self.ser.readline()).strip("\\n\\rb'").split(' ')
                    if len(data) == 3:
                        json = {
                            "date": datetime.now().strftime("%d/%m/%Y"),
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "humidity": float(data[0]),
                            "temperature": float(data[1]),
                            "moisture_soil_perc": int(data[2])
                        }
                        print(json)


if __name__ == '__main__':
    br = Bridge()
    br.loop()
