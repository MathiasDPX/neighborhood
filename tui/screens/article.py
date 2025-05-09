from textual.widgets import Label, Header, MarkdownViewer, Footer
from textual.app import ComposeResult
from textual.screen import Screen
import bridge

class ArticleScreen(Screen):
    CSS = """
        
    """

    def __init__(self, id:int):
        self.article_id = id
        self.data = bridge.get_article(self.article_id)

        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header()

        yield Label(f"{self.data['title']}")
        yield Label(f"@{self.data['author']}")
        yield Label("")
        yield MarkdownViewer(self.data['body'])

        yield Footer()