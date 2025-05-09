from textual.widgets import Header
from textual.app import App, ComposeResult
from screens import *

class Router(App):
    TITLE = "HackBlogger"
    
    BINDINGS = [
        ("ctrl+h", "push_screen('home')", "Home")
    ]
    
    def compose(self) -> ComposeResult:
        yield Header()

    def on_mount(self) -> None:
        self.install_screen(HomeScreen(), name="home")
        self.push_screen("home")

if __name__ == "__main__":
    app = Router()
    app.run()