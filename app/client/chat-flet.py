from chatcli import *


import flet as ft


TARGET_IP = os.getenv("SERVER_IP") or "127.0.0.1"
TARGET_PORT = os.getenv("SERVER_PORT") or "8889"
ON_WEB = os.getenv("ONWEB") or "0"


def main(page):
    cc = ChatClient()
    page.title = "Chat App"
    is_login = False

    global login_dialog
    def login_dialog():
        nonlocal is_login
        global signin
        global logouttologin
        global changeto_logout

        def register(e):
            page.dialog.title=ft.Text(
                "Register Now", style=ft.TextThemeStyle.TITLE_MEDIUM
            )
            page.dialog.actions=[
                ft.Row(controls=[ft.Text(value="Already have an account?"),ft.TextButton(text="Sign in",on_click=signin)],alignment=ft.MainAxisAlignment.CENTER),
                ft.ElevatedButton("Register", on_click=register_click)
            ]
            page.dialog.content=ft.Column([username, password,name,country], tight=True)
            page.update()
        
        def signin(e):
            page.dialog.title=ft.Text(
                "Login", style=ft.TextThemeStyle.TITLE_MEDIUM
            )
            page.dialog.actions=[
                ft.Row(controls=[ft.Text(value="Don't have a account?"),ft.TextButton(text="Sign Up Here",on_click=register)],alignment=ft.MainAxisAlignment.CENTER),
                ft.ElevatedButton("Login" ,width=100,height=30, on_click=login_click)
            ]
            page.dialog.content=ft.Column([username, password], tight=True)

            page.update()


        page.dialog = ft.AlertDialog(
            open=not is_login,
            modal=True,
            title=ft.Text(
                "Login", style=ft.TextThemeStyle.TITLE_MEDIUM
            ),
            content=ft.Column([username, password], tight=True),
            actions=[
                ft.Row(controls=[ft.Text(value="Don't have a account?"),ft.TextButton(text="Sign Up Here",on_click=register)],alignment=ft.MainAxisAlignment.CENTER),
                ft.ElevatedButton("Login",width=100,height=30, on_click=login_click)
            ],
            actions_alignment="end",
        )

    def register_click(__e__):
        if not username.value:
            username.error_text = "Enter a username for your profile."
            username.update()
        else :
            username.error_text = ""
            username.update()

        if not password.value:
            password.error_text = "You need to enter a password."
            password.update()
        else :
            password.error_text = ""
            password.update()
        
        if not name.value:
            name.error_text = "Enter a name for your profile"
            name.update()
        else :
            name.error_text = ""
            name.update()

        if not country.value:
            country.error_text = "Country cannot be blank!"
            country.update()
        else :
            country.error_text = ""
            country.update()

        if username.value != "" and password.value != "" and name.value != "" and country.value != "":
            login = cc.register(name.value, country.value, username.value, password.value)

            if "Error" in login:
                country.error_text = "Register Failed :("
                country.update()

            else:
                username.value = ""
                password.value = ""
                name.value = ""
                country.value = ""
                username.error_text = ""
                password.error_text = ""
                name.error_text = ""
                country.error_text = ""
                page.update()
                signin(None)
            page.update()

    def login_click(__e__):
        if not username.value:
            username.error_text = "Username connot be blank!"
            username.update()
        else :
            username.error_text = ""
            username.update()


        if not password.value:
            password.error_text = "Please enter password!"
            password.update()
        else :
            password.error_text = ""
            password.update()

        if username.value != "" and password.value != "":
            login = cc.login(username.value, password.value)

            if "Error" in login:
                username.error_text = "Username or Password does not match"
                password.error_text = "Username or Password does not match"
                username.update()
            else:
                username.value = ""
                password.value = ""
                username.error_text = ""
                password.error_text = ""
                is_login = True
                page.dialog.open = False

            page.update()

    username = ft.TextField(label="Username", autofocus=True)
    password = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        autofocus=True,
        on_submit=login_click,
    )
    name = ft.TextField(label="Name", autofocus=True)
    country = ft.TextField(label="Country", autofocus=True)
    
    login_dialog()

    def btn_click(e):
        if not cmd.value:
            cmd.error_text = "masukkan command"
            page.update()
        else:
            txt = cmd.value
            lv.controls.append(ft.Text(f"command: {txt}"))
            txt = cc.proses(txt)
            lv.controls.append(ft.Text(f"result {cc.tokenid}: {txt}"))
            cmd.value=""
            page.update()

    lv = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)
    cmd = ft.TextField(label="Your command")

    # page.add(lv)
    # page.add(cmd, ft.ElevatedButton("Send", on_click=btn_click))
    # Menu buttons grid for main menu
    def menu_buttons():
        return ft.GridView(
            spacing=10,
            runs_count=2,
            child_aspect_ratio=1.0,
            max_extent=250,
            controls= [
                ft.ElevatedButton( 
                        content=ft.Column(
                            [
                                ft.Icon(name=ft.icons.CHAT, size=100),
                                ft.Text(value="Private Chats", text_align=ft.TextAlign.CENTER, style=ft.TextThemeStyle.TITLE_MEDIUM)
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        width=150,
                        on_click=lambda _: page.go("/chat"),
                        style=ft.ButtonStyle(
                            shape={ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=2)}
                        )
                    ),
                ft.ElevatedButton( 
                        content=ft.Column(
                            [
                                ft.Icon(name=ft.icons.GROUP, size=100),
                                ft.Text(value="Group Chats", text_align=ft.TextAlign.CENTER, style=ft.TextThemeStyle.TITLE_MEDIUM)
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        width=250,
                        on_click=lambda _: page.go("/chat"),
                        style=ft.ButtonStyle(
                            shape={ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=2)}
                        )
                    ),
                ft.ElevatedButton( 
                        content=ft.Column(
                            [
                                ft.Icon(name=ft.icons.GROUPS, size=100),
                                ft.Text(value="Create Group Chat", text_align=ft.TextAlign.CENTER, style=ft.TextThemeStyle.TITLE_MEDIUM)
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        width=250,
                        on_click=lambda _: page.go("/chat"),
                        style=ft.ButtonStyle(
                            shape={ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=2)}
                        )
                    ),
                ft.ElevatedButton( 
                        content=ft.Column(
                            [
                                ft.Icon(name=ft.icons.GROUP_ADD, size=100),
                                ft.Text(value="Join Group Chat", text_align=ft.TextAlign.CENTER, style=ft.TextThemeStyle.TITLE_MEDIUM)
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        width=250,
                        height=250,
                        on_click=lambda _: page.go("/chat"),
                        style=ft.ButtonStyle(
                            shape={ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=2)}
                        )
                    ),
                ft.ElevatedButton( 
                        content=ft.Column(
                            [
                                ft.Icon(name=ft.icons.LOGOUT, size=100),
                                ft.Text(value="Logout", text_align=ft.TextAlign.CENTER, style=ft.TextThemeStyle.TITLE_MEDIUM)
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        width=250,
                        height=250,
                        on_click=lambda _: page.go("/chat"),
                        style=ft.ButtonStyle(
                            shape={ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=2)}
                        )
                    ),
            ]
        )
    
    def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    ft.AppBar(title=ft.Text("Chat Gaptek"), bgcolor=ft.colors.SURFACE_VARIANT),
                    ft.Text(f"Hi, User Gaptek!", style=ft.TextThemeStyle.HEADLINE_LARGE),
                    menu_buttons()
                ],
            )
        )
        if page.route == "/chat":
            page.views.append(
                ft.View(
                    "/chat",
                    [
                        ft.AppBar(title=ft.Text("Chat"), bgcolor=ft.colors.SURFACE_VARIANT),
                        lv,
                        cmd,
                        ft.ElevatedButton("Send", on_click=btn_click),
                    ],
                )
            )
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


if __name__=='__main__':
    if (ON_WEB=="1"):
        ft.app(target=main,view=ft.WEB_BROWSER,port=9999)
    else:
        ft.app(target=main)
