import flet as ft
import requests
from requests.auth import HTTPBasicAuth
from components import *
from os import getenv
from dotenv import load_dotenv

load_dotenv()


class MainPage(ft.UserControl):
    def __init__(self, page: ft.Page):
        page.title = "Register"
        page.expand = True
        page.scroll = True
        super().__init__()

        self.page = page

    def build(self):

        return ft.Row(
            [
                RegistrationSelector(
                    self.page.go, height=self.page.window_height * 0.80, width=self.page.window_width)
            ]
        )


class LoginPage(ft.UserControl):
    def __init__(self, page: ft.Page):
        page.title = "Login"
        page.expand = True
        page.scroll = True
        super().__init__()

        self.page = page

    def build(self):
        self.registerNumber = ft.Ref[ft.TextField]()
        self.password = ft.Ref[ft.TextField]()
        return ft.Column(
            [
                ft.TextField(label="Register Number", width=300,
                             ref=self.registerNumber),
                ft.TextField(label="Password", width=300,
                             password=True, can_reveal_password=True, ref=self.password),
                ft.FilledButton(text="Login", width=300,
                                on_click=self.onSubmit),
            ], spacing=10, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, width=self.page.window_width, height=self.page.window_height * 0.80
        )

    def onSubmit(self, e: ft.ControlEvent):
        res = requests.post(f"http://{getenv('HOST_HTTP')}:{getenv('PORT_HTTP')}/admin/login", json={}, auth=HTTPBasicAuth(
            self.registerNumber.current.value, self.password.current.value))
        if res.status_code == 200:
            self.page.session.set("user", self.registerNumber.current.value)
            self.page.go("/")
        elif res.status_code == 401:
            self.page.snack_bar = ErrorMessageBox("Wrong User or Password")
            self.page.snack_bar.open = True
            self.page.update()
        else:
            self.page.snack_bar = ErrorMessageBox("Error in Login")
            self.page.snack_bar.open = True
            self.page.update()


class UserPage(ft.Row):
    def __init__(self, page: ft.Page, file_ref: ft.Ref[ft.FilePicker]) -> None:

        page.title = "Security System | Users"
        self.navigation = ft.Ref[ft.NavigationRail]()
        self.previous = 0
        self.file_ref = file_ref
        super().__init__([
            ft.NavigationRail(on_change=self.onChange, selected_index=self.previous, label_type=ft.NavigationRailLabelType.ALL, ref=self.navigation,
                              height=500,
                              min_width=100,
                              min_extended_width=400, destinations=[
                                  ft.NavigationRailDestination(
                                      label="Add", icon=ft.icons.PERSON_ADD_ALT_1_OUTLINED),
                                  ft.NavigationRailDestination(
                                      label="Edit", icon=ft.icons.EDIT_OUTLINED),
                                  ft.NavigationRailDestination(
                                      label="Delete", icon=ft.icons.PERSON_REMOVE_ALT_1_OUTLINED),
                                  ft.NavigationRailDestination(
                                      label="Add Car", icon=ft.icons.DIRECTIONS_CAR_ROUNDED),
                                  ft.NavigationRailDestination(
                                      label="Edit Car", icon=ft.icons.CAR_CRASH),
                                  ft.NavigationRailDestination(label="Delete Car", icon=ft.icons.DIRECTIONS_CAR_OUTLINED),]),
            AddForm("user", page.go, file_ref),
        ], spacing=5, alignment=ft.MainAxisAlignment.START)

    def onChange(self, e: ft.ControlEvent):
        if e.control.disabled:
            self.navigation.current.selected_index = self.previous
            return

        index = int(e.data)
        self.controls.pop()
        self.navigation.current.disabled = True
        self.navigation.current.update()
        self.previous = index
        if index == 0:
            self.controls.append(
                AddForm("user", self.page.go, self.file_ref))
        elif index == 1:
            self.controls.append(
                EditForm("Register Number", "user", self.page.go))
        elif index == 2:
            self.controls.append(DeleteForm("Register Number", "user"))
        elif index == 3:
            self.controls.append(AddForm("vehicle", self.page.go))
        elif index == 4:
            self.controls.append(EditForm("Plate", "vehicle", self.page.go))
        elif index == 5:
            self.controls.append(DeleteForm("Plate", "vehicle"))
        else:
            self.controls.append(ft.Text("No Found"))
        self.navigation.current.disabled = False
        self.navigation.current.update()
        self.update()


class EmployePage(ft.Row):
    def __init__(self, page: ft.Page):
        page.title = "Security System | Employes"
        self.navigation = ft.Ref[ft.NavigationRail]()
        self.previous = 0
        super().__init__([
            ft.NavigationRail(on_change=self.onChange, selected_index=self.previous, label_type=ft.NavigationRailLabelType.ALL, ref=self.navigation,
                              # extended=True,
                              height=500,
                              min_width=100,
                              min_extended_width=400, destinations=[
                                  ft.NavigationRailDestination(
                                      label="Add", icon=ft.icons.PERSON_ADD_ALT_1_OUTLINED),
                                  ft.NavigationRailDestination(
                                      label="Edit", icon=ft.icons.EDIT_OUTLINED),
                                  ft.NavigationRailDestination(
                                      label="Delete", icon=ft.icons.PERSON_REMOVE_ALT_1_OUTLINED)]),
            AddForm("employe", page.go),
        ], spacing=5, alignment=ft.MainAxisAlignment.START)

    def onChange(self, e: ft.ControlEvent):
        if e.control.disabled:
            self.navigation.current.selected_index = self.previous
            return

        index = int(e.data)
        self.controls.pop()
        self.navigation.current.disabled = True
        self.navigation.current.update()
        self.previous = index
        if index == 0:
            self.controls.append(
                AddForm("employe", self.page.go))
        elif index == 1:
            self.controls.append(
                EditForm("Register Number", "employe", self.page.go))
        elif index == 2:
            self.controls.append(DeleteForm("Register Number", "employe"))
        else:
            self.controls.append(ft.Text("No Found"))
        self.navigation.current.disabled = False
        self.navigation.current.update()
        self.update()
