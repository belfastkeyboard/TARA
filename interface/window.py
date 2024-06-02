import os

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QSize, Qt
from pathlib import Path

from utils.error import error_dispatcher
from utils.system import DirectoryContents
from utils.status import info

from .util import DictionaryType
from .menu import TopBarMenu
from .tabs import TopBarTabs
from .dict import DictionaryMethods
from .process import Processes


class MainWindow(TopBarMenu, TopBarTabs, DictionaryMethods, Processes):

    def __init__(self, name: str, version: str) -> None:
        super().__init__()

        self.setWindowTitle(f"{name}——v{version}")
        self.setFixedSize(QSize(400, 320))
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        self._create_tabs()
        self._create_menu()

        error_dispatcher.error.connect(self.show_error_message)

        return

    @staticmethod
    def show_error_message(title: str, message: str) -> None:
        err = QMessageBox()
        err.setWindowTitle(title)
        err.setIcon(QMessageBox.Critical)
        err.setText(message)
        err.exec()

        return

    @staticmethod
    def _get_dictionary_items(to_load: DictionaryType) -> list[str]:
        dictionaries: DirectoryContents
        path: Path

        path = Path('resources' if to_load == DictionaryType.AVAILABLE else 'dictionaries')

        dictionaries = DirectoryContents([Path(path, item) for item in os.listdir(path)])
        dictionaries.clear_except('.txt')

        return [item.name for item in dictionaries]


def interface_init(name: str, version: str) -> None:
    info(f"Launching {name}\tv{version}!")

    app = QApplication([])
    app.setApplicationName(name)
    app.setApplicationVersion(version)

    window = MainWindow(name, version)
    window.show()
    app.exec()

    info(f"Closing {name}.")

    return
