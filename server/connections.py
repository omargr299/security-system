import re
from recognizers import plates
import hashlib
from socket import timeout
from time import sleep
import cv2
import numpy as np
import messages as msg
import recognizers.face as face
import recognizers.qr as qr
from db import models
from db import base
import threading as th
from recognizers.face import regist

from os import getenv
from dotenv import load_dotenv


load_dotenv()


class Connection:
    def __init__(self, socket, addr):
        self.socket = socket
        self.addr = addr

    def handle(self):
        pass


class DetectorConn(Connection):
    def __init__(self, socket, addr, service, user, database_user, datatbase_password):
        super().__init__(socket, addr)
        self.service = service
        self.database = DatabaseConn(database_user, datatbase_password)
        self.user = user

    def handle(self, message):

        super().handle()
        if message == msg.MessageTypes.Image.value:
            try:
                size = self.socket.recv(4)
                sleep(0.01)
                size = int.from_bytes(size, "little")
                buffer = bytes()
                while size > 0:
                    buffer += self.socket.recv(1024)
                    size -= 1024
            except timeout:
                return
            except Exception as e:
                raise e

            # decode to image
            if len(buffer) < 1024:
                return
            nparr = np.fromstring(buffer, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                return

            cv2.imshow("server img", img)
            cv2.waitKey(1)

            if self.service == msg.Service.Face.value:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                label = face.recognize(img)
                self.socket.send(
                    msg.MessageTypes.Sending.value.encode('utf-8'))
                sleep(0.01)
                isAutorized = not label < 0
                self.socket.send(str(isAutorized).encode('utf-8'))
                sleep(0.01)
            elif self.service == msg.Service.QR.value:
                qr_value = qr.read_value(img)
                self.socket.send(
                    msg.MessageTypes.Sending.value.encode('utf-8'))
                sleep(0.01)
                qr_id = self.database.getQR(qr_value)
                exists = qr_id is not None
                self.socket.send(str(exists).encode('utf-8'))
                sleep(0.01)
            elif self.service == msg.Service.Plates.value:
                plate_text = plates.read(img)
                self.socket.send(
                    msg.MessageTypes.Sending.value.encode('utf-8'))
                sleep(0.01)
                vehicle = self.database.getVehicle(plate_text)
                exists = vehicle is not None
                if exists:
                    if "users" in vehicle:
                        exists = vehicle["users"] > 0
                self.socket.send(str(exists).encode('utf-8'))
                print(exists)
                sleep(0.01)


class DatabaseConn():
    def __init__(self, user, password) -> None:
        self.session = base.create_session(user, password)

    def serializeUser(self, user: models.User):
        user.vehicles
        user_dict = user.__dict__.copy()
        user_dict.pop('_sa_instance_state')
        if "id" in user_dict:
            user_dict["id"] = user_dict["id"].__str__()
        if "face" in user_dict:
            user_dict.pop('face')
        if 'vehicles' in user_dict:
            vehicles = user.vehicles
            user_dict["vehicles"] = list(
                map(lambda x: self.serializeVehicle(x), vehicles))
        user_dict["qr"] = user.qr.hashCode
        return user_dict

    def serializeVehicle(self, vehicle: models.Vehicle):
        vehicle.users
        vehicle_dict = vehicle.__dict__.copy()
        vehicle_dict.pop('_sa_instance_state')
        if "id" in vehicle_dict:
            vehicle_dict["id"] = vehicle_dict["id"].__str__()

        if 'users' in vehicle_dict:
            vehicle_dict['users'] = len(list(vehicle_dict['users']))
        return vehicle_dict

    def serializeEmploye(self, employe: models.Employe):
        employe_dict = employe.__dict__.copy()
        employe_dict.pop('_sa_instance_state')
        if "id" in employe_dict:
            employe_dict.pop('id')
        if "password" in employe_dict:
            employe_dict.pop('password')
        return employe_dict

    def createUser(self, name, lastname, registerNumber, email="", plate=None, faces=None):

        user = self.session.query(models.User).where(
            models.User.registerNumber == registerNumber).first()
        if user is not None:
            raise Exception("User already exists")
        if type(name) != str or type(lastname) != str:
            raise Exception("Invalid name or lastname")
        if len(name) < 2 or len(lastname) < 2:
            raise Exception("Invalid name or lastname")
        name = name[0].upper()+name[1:].lower()
        lastname = lastname[0].upper()+lastname[1:].lower()
        user = models.User(name=name, lastname=lastname,
                           registerNumber=registerNumber)
        if email:
            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
            if (re.fullmatch(regex, email)):
                user.email = email
            else:
                raise Exception("Invalid email")
        self.session.add(user)
        self.session.commit()
        qr_hash = hash(user.registerNumber+getenv("SECRET"))
        qr_code = models.QR(hashCode=qr_hash, userId=user.id)
        self.session.add(qr_code)
        self.session.commit()
        user.qr = qr_code
        qr_img = qr.create(qr_hash)
        qr_base64 = qr.to_base64(qr_img)

        if faces:
            face = models.Face(userId=user.id)
            self.session.add(face)
            self.session.commit()
            user.face = face
            if user.face.label:
                th.Thread(target=regist, args=(
                    faces,
                    user.face.label, int(face.label)-1)).start()

        if plate:
            plate = plate.upper()
            vehicle = self.session.query(models.Vehicle).where(
                models.Vehicle.plate == plate).first()
            user.vehicles.add(vehicle)
            self.session.commit()

        resp = {
            "id": user.id.__str__(),
            "name": user.name,
            "lastname": user.lastname,
            "registerNumber": user.registerNumber,
            "qr": qr_base64
        }
        if user.vehicles:
            resp["vehicles"] = list(
                map(lambda x: self.serializeVehicle(x), user.vehicles))
        return resp

    def createVehicle(self, plate, brand=None, model=None, color=None):
        plate = plate.upper()
        vehicle = self.session.query(models.Vehicle).where(
            models.Vehicle.plate == plate).first()
        if vehicle is not None:
            raise Exception("Vehicle already exists")
        vehicle = models.Vehicle(
            plate=plate, brand=brand, model=model, color=color)
        self.session.add(vehicle)
        self.session.commit()
        return self.serializeVehicle(vehicle)

    def createEmploye(self, name, lastname, registerNumber, password, role):
        employe = self.session.query(models.Employe).where(
            models.Employe.registerNumber == registerNumber).first()
        if employe is not None:
            raise Exception("Employe already exists")
        if role != "admin" and role != "operator":
            raise Exception("Invalid role")
        if type(name) != str or type(lastname) != str:
            raise Exception("Invalid name or lastname")
        if len(name) < 2 or len(lastname) < 2:
            raise Exception("Invalid name or lastname")
        if type(password) != str:
            raise Exception("Invalid password")
        if len(password) < 7 or len(password) > 15:
            raise Exception("Invalid password")

        name = name[0].upper()+name[1:].lower()
        password = hashlib.sha256(
            password.encode('utf-8')+getenv("SECRET").encode('utf-8')).hexdigest()
        lastname = lastname[0].upper()+lastname[1:].lower()
        employe = models.Employe(name=name, lastname=lastname,
                                 registerNumber=registerNumber, password=password, role=role)
        self.session.add(employe)
        self.session.commit()

        return self.serializeEmploye(employe)

    def getAllUsers(self):
        res = self.session.query(models.User).all()
        res = list(map(lambda x: self.serializeUser(x), res))

        return res

    def getAllVehicles(self):
        res = self.session.query(models.Vehicle).all()
        res = list(map(lambda x: self.serializeVehicle(x), res))

        return res

    def getAllEmployes(self):
        employes = self.session.query(models.Employe).all()
        employes = list(
            map(lambda employe: self.serializeEmploye(employe), employes))

        return employes

    def getUser(self, registerNumber):
        user = self.session.query(models.User).where(
            models.User.registerNumber == registerNumber).first()
        if user is None:
            return
        return self.serializeUser(user)

    def getVehicle(self, plate: str):
        if type(plate) != str:
            return
        res = self.session.query(models.Vehicle).where(
            models.Vehicle.plate == plate.upper()).first()
        if res is None:
            return
        return self.serializeVehicle(res)

    def getEmploye(self, registerNumber, modifingNumber):
        employe = self.session.query(models.Employe).where(
            models.Employe.registerNumber == registerNumber).first()
        if employe is None:
            return
        if employe.role == "admin":
            if employe.registerNumber != modifingNumber:
                raise PermissionError("Not authorized")

        return self.serializeEmploye(employe)

    def getUserById(self, id):
        res = self.session.query(models.User).where(
            models.User.id == id).first()
        if res is None:
            return
        return self.serializeUser(res)

    def updateUser(self, registerNumber, name="", lastname="", email="", plate="", faces=None):
        user = self.session.query(models.User).where(
            models.User.registerNumber == registerNumber).one_or_none()
        if user is None:
            return
        if type(name) == str and len(name) >= 2:
            name = name[0].upper()+name[1:].lower()
            user.name = name
        if type(lastname) == str and len(lastname) >= 2:
            lastname = lastname[0].upper()+lastname[1:].lower()
            user.lastname = lastname
        if type(email) and len(email) > 0:
            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
            if (re.fullmatch(regex, email)):
                user.email = email
            else:
                raise Exception("Invalid email")
        if type(plate) == str and len(plate) > 0:
            plate = plate.upper()
            vehicle = self.session.query(models.Vehicle).where(
                models.Vehicle.plate == plate).first()
            if vehicle is None:
                raise Exception("Vehicle not found")
            if vehicle in user.vehicles:
                raise Exception("Vehicle already in possesion")
            user.vehicles.add(vehicle)
        if type(faces) == list and len(faces) >= 10:
            label = int(user.face.label)
            th.Thread(target=regist, args=(faces, label-1, True)).start()
        resp = self.serializeUser(user)
        self.session.commit()

        return resp

    def updateVehicle(self, plate: str, brand="", model="", color=""):
        res = self.session.query(models.Vehicle).where(
            models.Vehicle.plate == plate.upper()).one_or_none()
        if res is None:
            return
        if type(brand) == str and len(brand) > 2:
            res.brand = brand
        if type(model) == str and len(model) > 2:
            res.model = model
        if type(color) == str and len(color) > 2:
            res.color = color
        resp = self.serializeVehicle(res)
        self.session.commit()

        return resp

    def updateEmploye(self, registedNumber, modifingNumber, name="", lastname="", role="", password=""):

        employe = self.session.query(models.Employe).where(
            models.Employe.registerNumber == registedNumber).first()
        if employe is None:
            return False
        if employe.role == "admin":
            if employe.registerNumber != modifingNumber:
                raise PermissionError("Not authorized")
        if type(name) == str and len(name) >= 2:
            name = name[0].upper()+name[1:].lower()
            employe.name = name
        if type(lastname) == str and len(lastname) >= 2:
            lastname = lastname[0].upper()+lastname[1:].lower()
            employe.lastname = lastname
        if type(password) == str and len(password) > 7 and len(password) < 15:
            employe.password = hashlib.sha256(password.encode(
                'utf-8') + getenv("SECRET").encode('utf-8')).hexdigest()
        self.session.commit()
        return True

    def deleteUser(self, registerNumber):
        user = self.session.query(models.User).where(
            models.User.registerNumber == registerNumber).first()
        if user is None:
            return
        if user.face:
            label = user.face.label
            if label:
                face.unRegist(label)
        resp = self.serializeUser(user)
        self.session.delete(user)
        self.session.commit()

        return resp

    def deleteVehicle(self, plate: str):
        vehicle = self.session.query(models.Vehicle).where(
            models.Vehicle.plate == plate.upper()).first()
        if vehicle is None:
            return False
        self.session.delete(vehicle)
        self.session.commit()
        return True

    def deleteEmploye(self, registedNumber, modifingNumber):
        employe = self.session.query(models.Employe).where(
            models.Employe.registerNumber == registedNumber).first()
        if employe is None:
            return
        if employe.role == "admin":
            if employe.registerNumber != modifingNumber:
                raise PermissionError("Not authorized")
        resp = self.serializeEmploye(employe)
        self.session.delete(employe)
        self.session.commit()
        return resp

    def getQR(self, hashCode):
        if type(hashCode) != str:
            return
        res = self.session.query(models.QR).where(
            models.QR.hashCode == hashCode).first()
        if res is None:
            return
        return res.userId

    def isAuthorized(self, registerNumber, password):
        employe = self.session.query(models.Employe).where(
            models.Employe.registerNumber == registerNumber).first()
        if employe is None:
            return False
        password = hashlib.sha256(password.encode(
            'utf-8') + getenv("SECRET").encode('utf-8')).hexdigest()
        if employe.password != password:
            return False
        return True

    def isAdminAuthorized(self, registerNumber, password):
        employe = self.session.query(models.Employe).where(
            models.Employe.registerNumber == registerNumber).first()
        if employe is None:
            return False
        password = hashlib.sha256(password.encode(
            'utf-8') + getenv("SECRET").encode('utf-8')).hexdigest()
        if employe.password != password:
            return False
        if employe.role != "admin":
            return False
        return True
