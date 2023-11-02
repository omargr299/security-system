import re
import base64
from json import load
import os
from typing import Callable, Literal
import cv2
import numpy as np
import requests
from registers import face
import flet as ft
import requests
from requests.auth import HTTPBasicAuth
from os import getenv
from dotenv import load_dotenv
from pygrabber.dshow_graph import FilterGraph
filter = FilterGraph()

load_dotenv()


class ErrorMessageBox(ft.SnackBar):
    def __init__(self, message):
        super().__init__(ft.Text(message, color=ft.colors.WHITE), bgcolor=ft.colors.RED,
                         action="Ok", on_action=self.onOk)

    def onOk(self, e: ft.ControlEvent):
        self.open = False
        self.page.update()
        self.page.snack_bar = None


class SuccessMessageBox(ft.SnackBar):
    def __init__(self, message):
        super().__init__(ft.Text(message, color=ft.colors.WHITE), bgcolor=ft.colors.GREEN,
                         action="Ok", on_action=self.onOk)

    def onOk(self, e: ft.ControlEvent):
        self.open = False
        self.page.update()
        self.page.snack_bar = None


class Header(ft.Row):
    def __init__(self, title: str, logout: Callable, ref, height: int = 100):
        self.logout = logout
        super().__init__(
            [
                ft.Text(title, style=ft.TextThemeStyle.HEADLINE_SMALL),

            ],
            spacing=0, alignment=ft.MainAxisAlignment.SPACE_BETWEEN, height=height, ref=ref
        )

    def isLogged(self):
        islog = self.page.session.get("user") is not None
        if islog:
            if len(self.controls) == 1:
                self.controls.append(ft.TextButton(
                    "Logout", on_click=self.logout))
        else:
            if len(self.controls) > 1:
                self.controls.pop(1)


class backButton(ft.TextButton):
    def __init__(self, goTo: Callable):
        super().__init__(
            text="Back",
            icon="arrow_back",
            on_click=lambda e: goTo("/"),
        )


class RegistrationSelector(ft.Column):
    def __init__(self, goTo: Callable, height: int = 100, width: int = 100):
        super().__init__(
            [
                ft.ElevatedButton("Users", on_click=lambda e: goTo("/Users")),
                ft.ElevatedButton(
                    "Employes", on_click=lambda e: goTo("/Employes")),
            ],
            spacing=10, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, height=height, width=width
        )


class AuthModal(ft.AlertDialog):
    def __init__(self):
        self.action: Callable or None = None
        self.password = ft.Ref[ft.TextField]()
        super().__init__(content=ft.Column([
            ft.Text("Authorization Required"),
            ft.TextField(label="Password", width=300, password=True,
                         can_reveal_password=True, ref=self.password),
            ft.FilledButton(text="Continue", width=300,
                            on_click=self.onContinue),
            ft.TextButton(text="Cancel", on_click=self.onClose)],
            spacing=10, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ), modal=True, on_dismiss=self.onDimiss, actions_alignment=ft.MainAxisAlignment.CENTER)

    def onContinue(self, e: ft.ControlEvent):
        if not self.action:
            return
        user = self.page.session.get("user")
        password = self.password.current.value
        if password == "":
            self.password.current.error_text = "Password is required"
            self.password.current.update()
            return
        else:
            self.password.current.error_text = ""
            self.password.current.update()
        self.action(user, password)
        self.password.current.value = ""
        self.onClose(e)

    def onClose(self, e: ft.ControlEvent):
        self.page.dialog.open = False
        self.page.update()

    def onDimiss(self, e: ft.ControlEvent):
        self.page.update()


class Form(ft.Column):
    def serializeData(self):
        pass

    def setInfo(self, **kwargs):
        pass

    def onSubmit(self, user, password):
        pass

    def search(self, user, password):
        pass

    def onClick(self, e: ft.ControlEvent):
        self.page.dialog.open = True
        self.page.dialog.action = self.onSubmit
        self.page.update()

    def onSearch(self, e: ft.ControlEvent):
        self.page.dialog.open = True
        self.page.dialog.action = self.search
        self.page.update()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class BoolVar:
    def __init__(self, value: bool):
        self.value = value

    def set(self, value: bool):
        self.value = value

    def get(self):
        return self.value


class FaceScanner(ft.Column):
    def __init__(self, faces: list = []):
        self.cam = None
        self.image = ft.Ref[ft.Image]()
        self.progress = ft.Ref[ft.ProgressBar]()
        self.recording = BoolVar(False)
        self.pause = BoolVar(False)
        img = np.zeros((200, 200, 3), np.uint8)
        _, buffer = cv2.imencode('.jpg', img)
        self.default = base64.b64encode(buffer).decode("utf-8")
        self.faces = faces
        super().__init__(
            [
                ft.Text("Face"),
                ft.TextButton("Scan Face", on_click=self.Scan),
            ],
            spacing=10
        )

    def Scan(self, e: ft.ControlEvent):
        if self.cam:
            return
        self.controls.clear()
        self.controls.append(ft.Text("Face"))
        self.controls.append(
            ft.Row([
                ft.Text("Scanning..."),
                ft.ProgressBar(width=100, ref=self.progress)
            ])
        )
        self.devices = filter.get_input_devices()
        self.current_device = 4
        self.controls.append(ft.Dropdown(label="Camera", width=200,
                                         options=[ft.dropdown.Option(
                                             name) for name in self.devices],
                                         value=self.devices[self.current_device],
                                         on_change=self.changeCam))
        self.update()

        self.cam = cv2.VideoCapture(self.current_device, cv2.CAP_DSHOW)
        self.controls.append(ft.Image(src_base64=self.default, ref=self.image))
        self.controls.append(ft.ElevatedButton("Cancel", on_click=self.Cancel))
        self.update()

        self.recording.set(True)
        while self.recording.get():
            if self.pause.get():
                continue

            self.getFrame()
            if len(self.faces) >= 10:
                enconded_faces = list(map(lambda face: cv2.imencode(
                    '.jpg', face)[1].tobytes(), self.faces))
                enconded_faces = list(map(lambda face: base64.b64encode(
                    face).decode("utf-8"), enconded_faces))
                self.faces.clear()
                self.faces.extend(enconded_faces)
                self.controls[1].controls[0].value = "Done"
                self.controls.pop(2)
                self.controls.pop(2)
                self.page.snack_bar = SuccessMessageBox(
                    "Face scan succesfully")
                self.page.snack_bar.open = True
                self.page.update()
                break

    def getFrame(self):
        ret, frame = self.cam.read()
        if ret:
            cv2.resize(frame, (200, 200))
            face.capture(frame, self.faces)
            self.progress.current.value = len(self.faces)/10
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                img64 = base64.b64encode(buffer).decode("utf-8")
                self.image.current.src_base64 = img64
        self.update()

    def Cancel(self, e: ft.ControlEvent):
        self.recording.set(False)
        self.faces.clear()
        self.controls.clear()
        if self.cam:
            self.cam.release()
            self.cam = None
        self.controls.append(ft.Text("Face"))
        self.controls.append(ft.TextButton("Scan Face", on_click=self.Scan))
        self.page.snack_bar = SuccessMessageBox("Face scan canceled")
        self.page.snack_bar.open = True
        self.update()

    def changeCam(self, e: ft.ControlEvent):
        self.pause.set(True)
        self.cam.release()
        current_device = self.devices.index(e.data)
        self.cam = cv2.VideoCapture(current_device, cv2.CAP_DSHOW)
        self.page.update()
        self.pause.set(False)


class UserForm(Form):

    def serializeData(self, user, password):
        name = self.name.current.value.lower()
        name = name[0].upper() + name[1:]
        lastname = self.lastname.current.value.lower()
        lastname = lastname[0].upper() + lastname[1:]
        register_number = self.register_number.current.value
        post_data = {}

        post_data["name"] = name
        post_data["lastname"] = lastname
        post_data["registerNumber"] = register_number

        if self.email.current.value:
            post_data["email"] = self.email.current.value

        if self.vehicle.current.value:
            resp = self.search(user, password)
            if not resp:
                return
            post_data["plate"] = self.vehicle.current.value

        if self.faces and len(self.faces) >= 10:
            post_data["faces"] = self.faces

        return post_data

    def setInfo(self, **kwargs):
        if "name" in kwargs:
            self.name.current.value = kwargs["name"]
        if "lastname" in kwargs:
            self.lastname.current.value = kwargs["lastname"]
        if "email" in kwargs:
            self.email.current.value = kwargs["email"]

    def getVehicle(self, plate, user, password):
        plate = plate.upper()
        resp = requests.get(
            f"http://{getenv('HOST_HTTP')}:{getenv('PORT_HTTP')}/vehicle/{plate}", auth=HTTPBasicAuth(user, password))
        if resp.status_code != 200:
            return
        reps_json = resp.json()
        if "plate" not in reps_json:
            return
        return reps_json

    def search(self, user, password):
        if self.vehicle.current.value == " ":
            self.vehicle.current.error_text = "Vehicle is required"
            self.page.update()
            return
        resp = self.getVehicle(self.vehicle.current.value, user, password)
        if not resp:
            self.vehicle.current.error_text = "Vehicle not found"
            self.page.update()
            return

        self.page.snack_bar = SuccessMessageBox("Vehicle found")
        self.page.snack_bar.open = True
        return resp

    def comprobeEmail(self, e: ft.ControlEvent):
        email = self.email.current.value
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if (re.fullmatch(regex, email)):
            self.email.current.error_text = ""
            self.email.current.update()
            return True
        else:
            self.email.current.error_text = "Invalid email"
            self.email.current.update()
            return False

    def __init__(self, goTo: Callable, path, ref=None):
        self.name = ft.Ref[ft.TextField]()
        self.lastname = ft.Ref[ft.TextField]()
        self.register_number = ft.Ref[ft.TextField]()
        self.email = ft.Ref[ft.TextField]()
        self.vehicle = ft.Ref[ft.TextField]()
        self.faces = []
        self.plates = []
        self.path = path
        super().__init__(
            controls=[

                ft.TextField(label="Name", shift_enter=True, ref=self.name),
                ft.TextField(label="Last Name", shift_enter=True,
                             ref=self.lastname),
                ft.TextField(label="Regsiter Number",
                             shift_enter=True, ref=self.register_number),
                ft.TextField(label="Email", shift_enter=True,
                             ref=self.email, on_change=self.comprobeEmail),
                ft.Row([
                    ft.TextField(label="Vehicle", shift_enter=True,
                                 ref=self.vehicle),
                    ft.OutlinedButton("Search Vehicle",
                                      on_click=self.onSearch),
                ]),
                FaceScanner(self.faces),
            ],
            spacing=10, alignment=ft.MainAxisAlignment.START, ref=ref
        )


class VehicleForm(ft.Column):

    def serializeData(self, user, password):
        plate = self.plate.current.value.upper()
        brand = self.brand.current.value.lower()
        model = self.model.current.value.lower()
        color = self.color.current.value.lower()
        post_data = {}
        if plate:
            post_data["plate"] = plate
            if brand:
                post_data["brand"] = brand
            if model:
                post_data["model"] = model
            if color:
                post_data["color"] = color
        return post_data

    def setInfo(self, **kwargs):
        if "plate" in kwargs:
            self.plate.current.value = kwargs["plate"]
        if "brand" in kwargs:
            self.brand.current.value = kwargs["brand"]
        if "model" in kwargs:
            self.model.current.value = kwargs["model"]
        if "color" in kwargs:
            self.color.current.value = kwargs["color"]

    def __init__(self, path, ref=None):
        self.plate = ft.Ref[ft.TextField]()
        self.brand = ft.Ref[ft.TextField]()
        self.model = ft.Ref[ft.TextField]()
        self.color = ft.Ref[ft.TextField]()

        super().__init__(
            controls=[
                ft.TextField(label="Plate", shift_enter=True, ref=self.plate),
                ft.TextField(label="Brand", shift_enter=True, ref=self.brand),
                ft.TextField(label="Model", shift_enter=True, ref=self.model),
                ft.TextField(label="Color", shift_enter=True, ref=self.color),

            ], spacing=10, alignment=ft.MainAxisAlignment.START, ref=ref)


class EmployesForm(ft.Column):
    def __init__(self, ref, editMode=False):
        self.name = ft.Ref[ft.TextField]()
        self.lastname = ft.Ref[ft.TextField]()
        self.register_number = ft.Ref[ft.TextField]()
        self.role = ft.Ref[ft.Dropdown]()
        self.password = ft.Ref[ft.TextField]()
        self.confirm_password = ft.Ref[ft.TextField]()
        self.editMode = editMode
        super().__init__(
            [
                ft.TextField(label="Name", shift_enter=True, ref=self.name),
                ft.TextField(label="Last Name", shift_enter=True,
                             ref=self.lastname),
                ft.TextField(label="Regsiter Number",
                             shift_enter=True, ref=self.register_number),
                ft.Dropdown(label="Role", options=[
                            ft.dropdown.Option(
                                "Admin"),
                            ft.dropdown.Option("Operator")], ref=self.role),
                ft.TextField(label="Password", password=True,
                             can_reveal_password=True, shift_enter=True, on_change=self.comparePasswords, ref=self.password),
                ft.TextField(label="Confirm Password", password=True,
                             can_reveal_password=True, shift_enter=True, on_change=self.comparePasswords, ref=self.confirm_password),
            ],
            spacing=10, alignment=ft.MainAxisAlignment.START, ref=ref
        )

    def comparePasswords(self, e: ft.ControlEvent):
        if self.editMode and self.password.current.value == "" and self.confirm_password.current.value == "":
            return True

        if len(self.password.current.value) < 7 or len(self.password.current.value) > 15:
            self.password.current.error_text = "Password must be at least 7 or most 15 characters"
            self.password.current.update()
            return False
        else:
            self.password.current.error_text = ""
            self.password.current.update()

        if self.password.current.value != self.confirm_password.current.value:
            self.confirm_password.current.error_text = "Passwords don't match"
            self.confirm_password.current.update()
            return False
        else:
            self.confirm_password.current.error_text = ""
            self.confirm_password.current.update()
        return True

    def serializeData(self, user="", password=""):
        if not self.comparePasswords(None):
            return

        name = self.name.current.value.lower()
        name = name[0].upper() + name[1:]
        lastname = self.lastname.current.value.lower()
        lastname = lastname[0].upper() + lastname[1:]
        register_number = self.register_number.current.value
        post_data = {}

        post_data["name"] = name
        post_data["lastname"] = lastname
        post_data["registerNumber"] = register_number
        post_data["role"] = self.role.current.value.lower()
        post_data["password"] = self.password.current.value

        return post_data

    def setInfo(self, **kwargs):
        if "name" in kwargs:
            self.name.current.value = kwargs["name"]
        if "lastname" in kwargs:
            self.lastname.current.value = kwargs["lastname"]
        self.register_number.current.disabled = True
        if "role" in kwargs:
            self.role.current.value = kwargs["role"]


class AddForm(Form):
    def __init__(self, entiety: Literal["user", "vehicle", "employe"], togo=Callable, file_ref: ft.Ref[ft.FilePicker] = None):
        if type(entiety) != str:
            raise TypeError("entiety must be a string")

        self.refForm = ft.Ref[UserForm or VehicleForm or EmployesForm]()
        self.entiety = entiety.lower()
        self.file_ref = file_ref
        form = None
        if self.entiety == "user":
            form = UserForm(togo, self.entiety, self.refForm)
        elif self.entiety == "vehicle":
            form = VehicleForm(self.entiety, self.refForm)
        elif self.entiety == "employe":
            form = EmployesForm(self.refForm)

        super().__init__(
            controls=[
                form,
                ft.ElevatedButton("Add", on_click=self.onClick),
            ],
            spacing=10, alignment=ft.MainAxisAlignment.START
        )

    def onSubmit(self, user, password):
        post_data = self.refForm.current.serializeData(user, password)
        if post_data is None:
            return False
        resp = requests.post(
            f"http://{getenv('HOST_HTTP')}:{getenv('PORT_HTTP')}/{self.entiety}s", json=post_data, auth=HTTPBasicAuth(user, password))
        if resp.status_code == 200:
            resp_json = resp.json()
            if "qr" in resp_json:
                base64_qr = resp_json["qr"]
                qr_buffer = base64.b64decode(base64_qr)

                def on_result(e: ft.FilePickerResultEvent):
                    with open(e.path, "wb") as f:
                        f.write(qr_buffer)
                self.file_ref.current.on_result = on_result
                self.file_ref.current.save_file(
                    'save qr', resp_json["registerNumber"]+".png", os.path.join(os.path.splitdrive(__file__)[0].upper()+'\\', 'Users', 'Public', 'Desktop'), ['*.png'])

            self.page.snack_bar = SuccessMessageBox(
                f"{self.entiety} added succesfully")
        else:
            self.page.snack_bar = ErrorMessageBox("Register fail")
        self.page.snack_bar.open = True
        # self.page.update()


class DeleteForm(Form):
    def __init__(self, label, entiety):
        if type(entiety) != str:
            raise TypeError("entiety must be a string")

        self.search_param = ft.Ref[ft.TextField]()
        self.entiety = entiety.lower()
        super().__init__(
            controls=[
                ft.TextField(label=label, shift_enter=True,
                             ref=self.search_param),
                ft.ElevatedButton("Delete", on_click=self.onClick),
            ],
            spacing=10, alignment=ft.MainAxisAlignment.START
        )

    def onSubmit(self, user, password):
        param = self.search_param.current.value
        res = requests.delete(
            f"http://{getenv('HOST_HTTP')}:{getenv('PORT_HTTP')}/{self.entiety}/{param}", auth=HTTPBasicAuth(user, password))
        if res.status_code == 404:
            self.search_param.current.error_text = "Not Found"
            self.search_param.current.update()
        elif res.status_code == 200:
            self.search_param.current.error_text = ""
            self.search_param.current.update()
            self.page.snack_bar = SuccessMessageBox(
                f"{self.entiety} deleted succesfully")
            self.page.snack_bar.open = True
            self.page.dialog.open = False
            self.page.update()
            if self.entiety == "employe":
                res_json = res.json()
                if "role" in res_json and res_json["role"] == "admin":
                    self.page.session.clear()
                    self.page.go("/Login")
        elif res.status_code == 401:
            self.page.snack_bar = ErrorMessageBox("You are not authorized")
            self.page.snack_bar.open = True
        else:
            self.page.snack_bar = ErrorMessageBox("Delete fail")
            self.page.snack_bar.open = True
        # self.page.update()


class EditForm(Form):
    def __init__(self, label, entiety: Literal["user", "vehicle", "employe"], goTo: Callable):
        if type(entiety) != str:
            raise TypeError("entiety must be a string")

        self.search_param = ft.Ref[ft.TextField]()
        self.refForm = ft.Ref[ft.Column]()
        self.goTo = goTo
        self.entiety = entiety.lower()
        identifers = {
            "user": "registerNumber",
            "vehicle": "plate",
            "employe": "registerNumber"
        }
        self.identifier = identifers[self.entiety]

        super().__init__(
            controls=[
                ft.TextField(label=label, shift_enter=True,
                             ref=self.search_param),
                ft.ElevatedButton("Search", on_click=self.onSearch),
            ],
            spacing=10, alignment=ft.MainAxisAlignment.START
        )

    def search(self, user, password):
        search_param = self.search_param.current.value
        res = requests.get(
            f"http://{getenv('HOST_HTTP')}:{getenv('PORT_HTTP')}/{self.entiety}/{search_param}", auth=HTTPBasicAuth(user, password))
        if res.status_code == 404:
            self.search_param.current.error_text = "Not Found"
            self.search_param.current.update()
            return
        elif res.status_code == 200:
            self.search_param.current.error_text = ""
            self.search_param.current.update()
            resp_json = res.json()
            self.setForm(resp_json)
            self.page.snack_bar = SuccessMessageBox(
                "Search succesfully"
            )
            self.page.snack_bar.open = True
            self.page.update()
            return res.json()
        elif res.status_code == 401:
            self.page.snack_bar = ErrorMessageBox("You are not authorized")
            self.page.snack_bar.open = True
        else:
            self.page.snack_bar = ErrorMessageBox("Search fail")
            self.page.snack_bar.open = True
            self.page.update()

    def setForm(self, info):
        if (len(self.controls) > 2):
            self.controls.pop()
            self.controls.pop()
        form = None
        if self.entiety == "user":
            form = UserForm(self.goTo, self.entiety, self.refForm)
        elif self.entiety == "vehicle":
            form = VehicleForm(self.entiety, self.refForm)
        elif self.entiety == "employe":
            form = EmployesForm(self.refForm, True)

        form.setInfo(**info)
        if self.entiety == "user":
            form.controls[2].disabled = True
            form.controls[2].visible = False
        self.controls.append(form)
        self.controls.append(ft.ElevatedButton("Edit", on_click=self.onClick))
        self.update()

    def onSubmit(self, user, password):
        post_data = self.refForm.current.serializeData(user, password)
        if self.entiety == "user":
            post_data.pop("registerNumber")
        elif self.entiety == "vehicle":
            post_data.pop("plate")
        elif self.entiety == "employe":
            post_data.pop("registerNumber")

        param = self.search_param.current.value
        res = requests.put(
            f"http://{getenv('HOST_HTTP')}:{getenv('PORT_HTTP')}/{self.entiety}/{param}", json=post_data, auth=HTTPBasicAuth(user, password))
        if res.status_code == 404:
            self.search_param.current.error_text = "Not Found"
            self.search_param.current.update()
        elif res.status_code == 200:
            self.search_param.current.error_text = ""
            self.search_param.current.update()
            self.page.snack_bar = SuccessMessageBox(
                f"{self.entiety} edited succesfully")
            self.page.snack_bar.open = True
        elif res.status_code == 401:
            self.page.snack_bar = ErrorMessageBox("You are not authorized")
            self.page.snack_bar.open = True
        else:
            self.page.snack_bar = ErrorMessageBox("Edit fail")
            self.page.snack_bar.open = True
        # self.page.update()
