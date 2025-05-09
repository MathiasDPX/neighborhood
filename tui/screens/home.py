from textual.widgets import ListItem, ListView, Label, Header
from textual.app import ComposeResult
from textual.screen import Screen
from screens import ArticleScreen
from textual.events import Key
from textual import on
import bridge

class HomeScreen(Screen):
    TITLE = "HackBlogger"

    def __init__(self):
        self.page = 0
        super().__init__()

    @on(ListView.Selected)
    def on_item_selected(self, event: ListView.Selected) -> None:
        if "article" in self.app.SCREENS.keys():
            del self.app.SCREENS["article"]

        id = int(event.item.children[0].id.replace("article-",""))
        articlescreen = ArticleScreen(id)
        self.app.push_screen(articlescreen)

    def list_refresh(self):
        listview:ListView = self.screen.get_child_by_type(ListView)
        listview.remove_children()

        articles = bridge.list_articles(offset=self.page*10)
        for article in articles:
            widget = ListItem(Label(article['title'], id=f"article-{article['id']}"), markup=True)
            listview.mount(widget)

    @on(Key)
    def keypress(self, event:Key):
        char = event.character
        if char == "k":
            self.page += 1
        elif char == "j":
            if self.page != 0:
                self.page -= 1

        if char in ["k","j"]:
            self.list_refresh()
            self.notify(f"Switch to page {self.page+1}", timeout=1)

    def on_mount(self) -> None:
        self.list_refresh()

    def compose(self) -> ComposeResult:
        yield Header()

        yield ListView(ListItem(Label("Loading...")))
        
        yield Label("j/k: Change page")