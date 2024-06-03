from enum import Enum
from pathlib import Path

from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QWidget

from utils.error import error_dispatcher
from utils.handle_file import discern_type_all, discern_type_scan, discern_type_spellcheck
from utils.system import filetype_in_directory


class DictionaryType(Enum):
    AVAILABLE = 0
    LOADED = 1


class DragNDropAll(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

        return

    def dropEvent(self, event: QDropEvent) -> None:
        if not filetype_in_directory(Path('dictionaries'), '.txt'):
            error_dispatcher.raise_error(
                'Dictionary not found',
                "No dictionaries found.\nUse 'Dictionary' tab to load dictionaries."
            )
            return

        for url in event.mimeData().urls():
            file = Path(url.toLocalFile())
            discern_type_all(file)
            
        return


class DragNDropSpell(DragNDropAll):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

    def dropEvent(self, event: QDropEvent):
        if not filetype_in_directory(Path('dictionaries'), '.txt'):
            error_dispatcher.raise_error(
                'Dictionary not found',
                "No dictionaries found.\nUse 'Dictionary' tab to load dictionaries."
            )
            return

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
