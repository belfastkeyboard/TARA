from enum import Enum
from pathlib import Path

from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QWidget

from utils.handle_file import discern_type_all, discern_type_spellcheck, discern_type_scan


class DictionaryType(Enum):
    AVAILABLE = 0
    LOADED = 1


class DragNDropAll(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file = Path(url.toLocalFile())
            discern_type_all(file)


class DragNDropSpell(DragNDropAll):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file = Path(url.toLocalFile())
            discern_type_spellcheck(file)


class DragNDropScan(DragNDropAll):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file = Path(url.toLocalFile())
            discern_type_scan(file)
