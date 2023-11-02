
import socket as sk
import threading as th
from time import sleep
import requests
import messages as msg
import keyboard as kb
import connections as conns
from requests.auth import HTTPBasicAuth
from os import getenv
from dotenv import load_dotenv

load_dotenv()

server = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
server.bind((getenv('HOST_SOCKET'), int(getenv('PORT_SOCKET'))))
server.listen(5)

detectors: list[conns.DetectorConn] = []

server.settimeout(1)


def Handle(conn: conns.DetectorConn):
    global detectors
    conn.socket.settimeout(2)
    while True:
        if kb.is_pressed('q'):
            break

        try:
            message = conn.socket.recv(15).decode('utf-8')
            sleep(0.1)
        except sk.timeout:
            sleep(0.1)
            continue
        except UnicodeDecodeError:
            conn.socket.send(msg.MessageTypes.Fail.value.encode('utf-8'))
            sleep(0.1)
            continue
        except Exception as e:
            break

        if message == msg.MessageTypes.Exit.value:
            break
        elif message == msg.MessageTypes.Service.value:
            password = conn.socket.recv(1024).decode('utf-8')
            sleep(0.01)
            resp = requests.post(f"http://{getenv('HOST_HTTP')}:{getenv('PORT_HTTP')}/operator/login", auth=HTTPBasicAuth(
                conn.user, password))
            if resp.status_code != 200:
                conn.socket.send(msg.MessageTypes.Fail.value.encode('utf-8'))
                sleep(0.01)
                conn.socket.close()
                continue
            conn.socket.send(msg.MessageTypes.Success.value.encode('utf-8'))
            service = conn.socket.recv(1024).decode('utf-8')
            sleep(0.01)
            if service not in msg.Service.getValues():
                conn.socket.send(msg.MessageTypes.Fail.value.encode('utf-8'))
                sleep(0.01)
            else:
                conn.service = service
                conn.socket.send(
                    msg.MessageTypes.Success.value.encode('utf-8'))
                sleep(0.01)
        elif message == msg.MessageTypes.Camera.value:
            password = conn.socket.recv(1024).decode('utf-8')
            sleep(0.01)
            resp = requests.post(f"http://{getenv('HOST_HTTP')}:{getenv('PORT_HTTP')}/operator/login", auth=HTTPBasicAuth(
                conn.user, password))
            if resp.status_code != 200:
                conn.socket.send(msg.MessageTypes.Fail.value.encode('utf-8'))
                sleep(0.01)
                conn.socket.close()
                continue
            conn.socket.send(msg.MessageTypes.Success.value.encode('utf-8'))
        else:
            try:
                conn.handle(message)
            except Exception as e:
                break

    detectors.remove(conn)


print("Server is running on port", getenv('PORT_SOCKET'))
while True:
    if kb.is_pressed('q'):
        break

    try:
        conn, address = server.accept()
    except sk.timeout:
        continue

    try:
        conn.send(msg.MessageTypes.Success.value.encode('utf-8'))
        sleep(0.1)

        conn.send(msg.MessageTypes.Login.value.encode('utf-8'))
        sleep(0.01)
        registedNumber = conn.recv(1024).decode('utf-8')
        sleep(0.01)
        password = conn.recv(1024).decode('utf-8')
        sleep(0.01)
        conn.send(msg.MessageTypes.Service.value.encode('utf-8'))
        sleep(0.01)
        # create a new task for each client
        service = conn.recv(1024).decode()
        sleep(0.1)
    except Exception as e:
        continue
    else:
        conn = conns.DetectorConn(
            conn, address, service, registedNumber, getenv('OPERATOR_NAME'), getenv('OPERATOR_PASSWORD'))
        resp = requests.post(f"http://{getenv('HOST_HTTP')}:{getenv('PORT_HTTP')}/operator/login", auth=HTTPBasicAuth(
            registedNumber, password))
        if resp.status_code != 200:
            conn.socket.send(msg.MessageTypes.Fail.value.encode('utf-8'))
            sleep(0.01)
            conn.socket.close()
            continue
        print(f"New connection from {address[0]}:{address[1]}")
        conn.socket.send(msg.MessageTypes.Success.value.encode('utf-8'))
        detectors.append(conn)
        th.Thread(target=Handle, args=(conn,)).start()

server.close()
