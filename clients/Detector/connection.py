from serial import Serial, SerialException
import serial.tools.list_ports as port_list
import socket
from flet import Page
from time import sleep
from dotenv import load_dotenv
from os import getenv

load_dotenv()


class Connection:
    def __init__(self, page: Page):
        self.page = page
        self.server = None

    def connect(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self.server.connect(
                    (getenv('HOST_SOCKET'), int(getenv('PORT_SOCKET'))))
                message = self.server.recv(1024).decode("utf-8")
                if message != "success":
                    raise ValueError("No connect succesfully")
            except:
                sleep(1)
            else:
                break
        self.server.settimeout(5)

    def exit(self):
        self.server.send("exit".encode("utf-8"))

    def disconnect(self):
        self.exit()
        self.server.close()

    def configServcie(self, registerNumber: str, password: str, service: str):
        if type(service) != str:
            raise TypeError("Service must be a string")

        message = self.server.recv(1024).decode("utf-8")
        if message == "login":
            self.server.send(registerNumber.encode("utf-8"))
            sleep(0.01)
            self.server.send(password.encode("utf-8"))
            sleep(0.01)
            message = self.server.recv(1024).decode("utf-8")
            sleep(0.01)
            if message == "service":
                self.server.send(service.encode("utf-8"))
                sleep(0.01)
                response = self.server.recv(1024).decode("utf-8")
                sleep(0.01)
                if response == "success":
                    return True

        return False

    def reconfigService(self, password, service: str):
        if type(service) != str:
            raise TypeError("Service must be a string")

        self.server.send("service".encode("utf-8"))
        sleep(0.01)
        auth = self.isAuthorized(password)
        if not auth:
            return False
        self.server.send(service.encode("utf-8"))
        sleep(0.01)
        response = self.server.recv(1024).decode("utf-8")
        sleep(0.01)
        return response == "success"

    def isAuthorized(self, password):
        self.server.send(password.encode("utf-8"))
        sleep(0.01)
        resp = self.server.recv(1024).decode("utf-8")
        sleep(0.01)
        if resp != "success":
            return False
        return resp == "success"

    def sendImage(self, buffer: bytes):
        self.server.send("image".encode("utf-8"))
        sleep(0.01)
        self.server.send(len(buffer).to_bytes(4, "little"))
        sleep(0.01)
        while len(buffer) > 0:
            self.server.send(buffer[:1024])
            buffer = buffer[1024:]


class MicroControllerConnection:
    def __init__(self):
        self.hw_sensor = None
        self.connect()

    def connect(self):
        ports = list(port_list.comports())
        for port in ports:
            try:
                hw_sensor = Serial(port=port.name, baudrate=9600)
            except SerialException:
                continue
            else:
                self.hw_sensor = hw_sensor
                break

    def send(self, autorized: bool):
        self.hw_sensor.write(b'1' if autorized else b'0')
