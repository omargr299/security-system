
from typing import Callable
import flet as ft
import cv2
import base64
from time import sleep
import connection as conn
import numpy as np
from detectors import qr
from detectors import face
from detectors import plates
import threading as th

from pygrabber.dshow_graph import FilterGraph
filter = FilterGraph()


class ErrorMessageBox(ft.SnackBar):
    def __init__(self, message):
        super().__init__(ft.Text(message, color=ft.colors.WHITE), bgcolor=ft.colors.RED,
                         action="Ok", on_action=self.onOk)

    def onOk(self, e: ft.ControlEvent):
        self.open = False
        self.page.update()
        self.page.snack_bar = None


class AuthModal(ft.AlertDialog):
    def __init__(self):
        self.action: Callable or None = None
        self.close_action: Callable or None = None
        self.password = ft.Ref[ft.TextField]()
        self.continueButton = ft.Ref[ft.FilledButton]()
        self.cancelButton = ft.Ref[ft.TextButton]()
        super().__init__(content=ft.Column([
            ft.Text("Authorization Required"),
            ft.TextField(label="Password", width=300, password=True,
                         can_reveal_password=True, ref=self.password),
            ft.FilledButton(text="Continue", width=300,
                            on_click=self.onContinue, ref=self.continueButton),
            ft.TextButton(text="Cancel", on_click=self.onClose, ref=self.cancelButton)],
            spacing=10, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ), modal=True, on_dismiss=self.onDimiss, actions_alignment=ft.MainAxisAlignment.CENTER)

    def onContinue(self, e: ft.ControlEvent):
        if not self.action:
            return
        self.continueButton.current.disabled = True
        self.cancelButton.current.disabled = True
        if self.password.current.value == "":
            self.password.current.error_text = "Password is required"
            self.password.current.update()
        else:
            self.password.current.error_text = ""
            self.password.current.update()
            self.action(self.password.current.value)
            self.onClose(e)
        self.continueButton.current.disabled = False
        self.cancelButton.current.disabled = False

    def onClose(self, e: ft.ControlEvent):
        self.page.dialog.open = False
        self.page.update()
        if self.close_action:
            self.close_action()

    def onDimiss(self, e: ft.ControlEvent):
        self.page.update()


class ConecctionBanner(ft.Banner):
    def __init__(self, retry: Callable):

        super().__init__(
            bgcolor=ft.colors.AMBER_100,
            leading=ft.Icon(ft.icons.WARNING_AMBER_ROUNDED,
                            color=ft.colors.AMBER, size=40),
            content=ft.Text(
                "Oops, there were some errors while trying to delete the file. What would you like me to do?",
                color=ft.colors.BLACK
            ),
            actions=[
                ft.TextButton(content=ft.Text(
                    "Retry", color=ft.colors.BLUE), on_click=retry),
                ft.TextButton(content=ft.Text(
                    "Ok", color=ft.colors.BLUE), on_click=self.ok),
            ],
        )

    def ok(self, e: ft.ControlEvent):
        self.open = False
        self.page.update()


class BoolVar:
    def __init__(self, value: bool):
        self.value = value

    def set(self, value: bool):
        self.value = value

    def get(self):
        return self.value


class Camera(ft.Column):
    def __init__(self, page: ft.Page, connection: conn.Connection, controller: conn.MicroControllerConnection):
        devices = filter.get_input_devices()
        current_device = 4
        cam = cv2.VideoCapture(current_device, cv2.CAP_DSHOW)

        default = np.zeros((200, 200, 3), dtype=np.uint8)
        default_img = np.zeros((160, 160, 3), dtype=np.uint8)

        self.pause = BoolVar(False)
        self.loop = BoolVar(True)
        self.controller = controller
        self.connection = connection
        connection.server.settimeout(5)

        def show_image(page: ft.Page, image: ft.Image):
            nonlocal service_menu, label_text, cam, connection, default_img, default
            while self.loop.get():
                if self.pause.get():
                    sleep(0.1)
                    continue

                ret, frame = cam.read()
                if ret:

                    img = default_img
                    cv2.resize(frame, (200, 200))
                    if service_menu.value == "Face":
                        faces = face.getFaces(frame)
                        if len(faces) > 0:
                            img = faces[0]["face"]
                    elif service_menu.value == "QR":
                        res_qr = qr.cut_qr(frame)
                        if res_qr is not None:
                            img = res_qr
                    elif service_menu.value == "Plates":
                        plate = plates.cut(frame)
                        if plate is not None:
                            img = plate

                    _, buffer = cv2.imencode('.jpg', frame)
                    image.src_base64 = base64.b64encode(buffer).decode("utf-8")
                    _, buffer = cv2.imencode('.jpg', img)
                    connection.sendImage(buffer)
                    message = connection.server.recv(1024).decode("utf-8")
                    sleep(0.01)
                    if message == "sending":
                        isAutorized = connection.server.recv(
                            1024).decode("utf-8")
                        sleep(0.01)
                        label_text.value = "Autorized" if isAutorized == "True" else "Not autorized"
                        if service_menu.value == "Face":
                            if len(faces) > 0:
                                rect = faces[0]["rectangle"]
                                color = (0, 255, 0) if isAutorized == "True" else (
                                    0, 0, 255)
                                cv2.rectangle(
                                    frame, (rect.left(), rect.top()), (rect.right(), rect.bottom()), color, 2)
                                _, buffer = cv2.imencode('.jpg', frame)
                                image.src_base64 = base64.b64encode(
                                    buffer).decode("utf-8")
                        if self.controller.hw_sensor:
                            self.controller.send(isAutorized == "True")
                    page.update()
                else:
                    break
            cam.release()

        def serviceChange(e: ft.ControlEvent):
            nonlocal service_menu, connection
            self.pause.set(True)
            sleep(2)

            def change(password):
                nonlocal service_menu, connection
                res = connection.reconfigService(password, e.data.lower())
                if not res:
                    self.page.snack_bar = ErrorMessageBox("Error in change")
                    self.page.snack_bar.open = True
                    self.page.update()
                    service_menu.value = ""
                page.update()
                sleep(0.1)
                self.pause.set(False)

            page.dialog = AuthModal()
            page.dialog.action = change
            page.dialog.close_action = lambda: self.pause.set(False)
            page.dialog.open = True
            page.update()

        def cameraChange(e: ft.ControlEvent):
            nonlocal cam, current_device, devices
            self.pause.set(True)

            def change(password):
                nonlocal cam, current_device, devices
                connection.server.send("camera".encode("utf-8"))
                sleep(0.01)
                if connection.isAuthorized(password):
                    cam.release()
                    current_device = devices.index(e.data)
                    cam = cv2.VideoCapture(current_device, cv2.CAP_DSHOW)
                else:
                    self.page.snack_bar = ErrorMessageBox("Error in change")
                    self.page.snack_bar.open = True
                    self.page.update()
                page.update()
                self.pause.set(False)
            page.dialog = AuthModal()
            page.dialog.action = change
            page.dialog.close_action = lambda: self.pause.set(False)
            page.dialog.open = True
            page.update()

        service_menu = ServiceMenu(serviceChange)
        cameras_menu = cameras_menu = CamerasMenu(
            devices, current_device, cameraChange)
        label_text = ft.Text("", size=20)
        image = ft.Image("")
        image.src_base64 = base64.b64encode(default).decode("utf-8")
        image_th = th.Thread(target=lambda: show_image(page, image))
        image_th.start()
        super().__init__(controls=[
            service_menu,
            cameras_menu,
            label_text,
            image
        ]
        )

    def kill(self):
        self.pause.set(True)
        sleep(1)
        self.loop.set(False)


class ServiceMenu(ft.Dropdown):
    def __init__(self, serviceChange):
        super().__init__(
            width=100,
            options=[
                ft.dropdown.Option("Face"),
                ft.dropdown.Option("QR"),
                ft.dropdown.Option("Plates"),
            ],
            value="Face",
            on_change=serviceChange,
        )


class CamerasMenu(ft.Dropdown):
    def __init__(self, devices, current_device, cameraChange):

        super().__init__(
            width=500,
            options=[ft.dropdown.Option(name) for name in devices],
            value=devices[current_device],
            on_change=cameraChange,)


class Header(ft.Row):
    def __init__(self, title: str, logout: Callable or None, kill: Callable = None):
        self.logout = logout
        self.kill = kill
        super().__init__(
            [
                ft.Text(title, style=ft.TextThemeStyle.HEADLINE_SMALL),
            ],
            spacing=0, alignment=ft.MainAxisAlignment.SPACE_BETWEEN, height=50
        )

    def isLogged(self):
        if self.page.session.get("user"):
            def click(e: ft.ControlEvent):
                self.kill()
                self.logout()
            self.controls.append(ft.TextButton("Logout", on_click=click))
        else:
            if len(self.controls) > 1:
                self.controls.pop()


class Login(ft.UserControl):
    def __init__(self, page: ft.Page, connection: conn.Connection):
        page.title = "Login"
        page.expand = True
        page.scroll = True
        super().__init__()

        self.page = page
        self.connection = connection

    def build(self):
        self.registerNumber = ft.Ref[ft.TextField]()
        self.password = ft.Ref[ft.TextField]()
        return ft.Column(
            [
                ft.TextField(label="Register Number", width=300,
                             ref=self.registerNumber),
                ft.TextField(label="Password", width=300,
                             password=True, ref=self.password, can_reveal_password=True),
                ft.FilledButton(text="Login", width=300,
                                on_click=self.onSubmit),
            ], spacing=10, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, width=self.page.window_width, height=self.page.window_height * 0.80
        )

    def onSubmit(self, e: ft.ControlEvent):
        registerNumber = self.registerNumber.current.value
        password = self.password.current.value
        if registerNumber == "":
            self.registerNumber.current.error_text = "Register Number is required"
            self.registerNumber.current.update()
            return
        else:
            self.registerNumber.current.error_text = ""
            self.registerNumber.current.update()
        if password == "":
            self.password.current.error_text = "Password is required"
            self.password.current.update()
            return
        else:
            self.password.current.error_text = ""
            self.password.current.update()
        success = self.connection.configServcie(
            registerNumber, password, "face")
        if success:
            self.page.route = "/"
            self.page.snack_bar = None
            self.page.session.set("user", registerNumber)
            self.page.update()
        else:
            self.page.snack_bar = ErrorMessageBox("Error in login")
            self.page.snack_bar.open = True
            self.page.update()
            self.connection.server.close()
            self.connection.connect()
