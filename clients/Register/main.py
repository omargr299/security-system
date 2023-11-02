from email import header
from weakref import ref
import flet as ft
from components import *
from pages import *


def main(page: ft.Page):
    page.title = "Register"
    page.expand = True
    page.scroll = True

    def changeRoute(e: ft.RouteChangeEvent):
        nonlocal page, file_ref
        if len(page.controls) > 1:
            for _ in range(len(page.controls)-1):
                page.controls.pop()

        header.current.isLogged()

        if e.route == "/":
            page.add(MainPage(page))
        elif e.route == "/Users":
            page.add(backButton(page.go))
            page.add(UserPage(page, file_ref))
        elif e.route == "/Employes":
            page.add(backButton(page.go))
            page.add(EmployePage(page))
        elif e.route == "/Settings":
            page.add(backButton(page.go))
            page.add(ft.Text("Settings"))
        elif e.route == "/Login":

            page.add(LoginPage(page))

        page.update()

    def Logout(e: ft.ControlEvent):
        page.session.clear()
        page.update()
        page.go("/Login")

    page.dialog = AuthModal()
    page.on_route_change = changeRoute

    file_ref = ft.Ref[ft.FilePicker]()
    pick_files_dialog = ft.FilePicker(
        ref=file_ref)
    page.overlay.append(pick_files_dialog)
    header = ft.Ref[Header]()
    page.add(Header("Register", Logout, height=page.window_height *
             0.10, ref=header))

    page.go("/Login")


ft.app(main)
