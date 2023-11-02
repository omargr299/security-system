
from time import sleep
import flet as ft

import components as cmp
import connection as conn
from pygrabber.dshow_graph import FilterGraph

filter = FilterGraph()


def main(page: ft.Page):
    page.title = "Flet counter example"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.expand = True
    page.scroll = True

    page.add(ft.Text("Loading..."))
    page.update()

    controller = conn.MicroControllerConnection()

    def tryconnect(e):
        controller.connect()
        if controller.hw_sensor:
            page.banner.open = False
            page.update()
    page.banner = cmp.ConecctionBanner(tryconnect)

    controller.connect()

    if not controller.hw_sensor:
        page.banner.open = True

    connection = conn.Connection(page)
    page.clean()
    page.update()

    def Logout():
        connection.exit()
        page.session.clear()
        page.go("/login")

    actions = []

    def End(code):
        for action in actions:
            action()
        Logout()
        page.close()
        exit(code)

    def routeChange(e: ft.RouteChangeEvent):
        actions.clear()
        page.clean()
        if e.route == "/":
            camera = cmp.Camera(page, connection, controller)
            actions.append(camera.kill)
            header = cmp.Header("Security system",
                                Logout, camera.kill)
            page.add(header)
            page.add(
                camera
            )
        elif e.route == "/login":
            header = cmp.Header("Security system", Logout)
            page.add(header)
            page.add(ft.Text("Loading..."))
            connection.connect()
            page.controls.pop()
            page.add(
                cmp.Login(page, connection)
            )
        header.isLogged()

    page.on_route_change = routeChange
    page.on_close = End
    page.go("/login")


ft.app(target=main)
