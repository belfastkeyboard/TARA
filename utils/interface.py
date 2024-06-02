import os

from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QLabel, QMessageBox, QAction, QFileDialog, QMenu, QStyle, QListWidget, QVBoxLayout,
    QHBoxLayout, QWidget, QPushButton, QTabWidget, QAbstractItemView
)
from PyQt5.QtCore import QSize, Qt, QUrl
from PyQt5.QtGui import QDropEvent, QDragEnterEvent, QDesktopServices
from pathlib import Path
from utils.handle_file import discern_type_all, discern_type_scan, discern_type_spellcheck
from utils.error import error_dispatcher
from utils.system import DirectoryContents, is_filetype, copy, delete, move
from enum import Enum


class DictionaryType(Enum):
    AVAILABLE = 0
    LOADED = 1


# TODO: create frames that only accept certain filetypes
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


# TODO: DragNDrop class for the scan tab
class DragNDropScan(DragNDropAll):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file = Path(url.toLocalFile())
            discern_type_scan(file)


class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("PyScanner")
        self.setFixedSize(QSize(400, 320))
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        self._create_tabs()
        self._create_menu()

        error_dispatcher.error.connect(self.show_error_message)

        return

    def _open_file(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self,
            'Open',
            '',  # add support for .docx files later
            'All files (*.jpg *.png *.txt *.pdf);;Images (*.jpg *.png);;Text (*.txt);;PDF (*.pdf)',
            options=QFileDialog.Options()
        )
        if files:
            for file in files:
                path = Path(file)
                discern_type_all(path)

        return

    def _open_scan(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self,
            'Open',
            '',  # add support for .docx files later
            'All files (*.jpg *.png *.pdf);;Images (*.jpg *.png);;PDF (*.pdf)',
            options=QFileDialog.Options()
        )
        if files:
            for file in files:
                path = Path(file)
                discern_type_scan(path)

        return

    def _open_spellcheck(self) -> None:
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(
            self,
            'Open',
            '',  # add support for .docx files later
            'All files (*.txt);;Text files (*.txt)',
            options=options
        )
        if files:
            for file in files:
                path = Path(file)
                discern_type_spellcheck(path)

        return

    def _create_menu(self) -> None:
        menu = self.menuBar()

        file = QMenu('&File', self)
        file.setFixedWidth(80)
        menu.addMenu(file)

        open_all = QAction('&Open', self)
        open_all.setShortcut('Ctrl+O')
        open_all.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        open_all.triggered.connect(self._open_file)
        file.addAction(open_all)

        return

    def _create_tabs(self) -> None:
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)
        tabs.setMovable(False)

        """ Quick Process Tab """
        tab_quick = QVBoxLayout()
        tab_quick.setAlignment(Qt.AlignCenter)

        label_quick = QLabel()
        label_quick.setText("Drag 'n' drop to process files.")

        button_quick = QPushButton()
        button_quick.setText("Open")
        button_quick.setMaximumWidth(50)
        button_quick.clicked.connect(self._open_file)

        tab_quick.addWidget(label_quick, alignment=Qt.AlignHCenter)
        tab_quick.addWidget(button_quick, alignment=Qt.AlignHCenter)

        container_quick = DragNDropAll()
        container_quick.setLayout(tab_quick)
        container_quick.setAcceptDrops(True)

        """ Scan Only Tab """
        tab_scan = QVBoxLayout()
        tab_scan.setAlignment(Qt.AlignCenter)

        label_scan = QLabel()
        label_scan.setText("Drag 'n' drop to scan files.")

        button_scan = QPushButton()
        button_scan.setText("Open")
        button_scan.setMaximumWidth(50)
        button_scan.clicked.connect(self._open_scan)  # TODO: self.open_scan

        tab_scan.addWidget(label_scan, alignment=Qt.AlignHCenter)
        tab_scan.addWidget(button_scan, alignment=Qt.AlignHCenter)

        container_scan = DragNDropScan()
        container_scan.setLayout(tab_scan)

        """ Spellchecking Tab """
        tab_spell = QVBoxLayout()
        tab_spell.setAlignment(Qt.AlignCenter)

        label_spell = QLabel()
        label_spell.setText("Drag 'n' drop to spellcheck files.")

        button_quick = QPushButton()
        button_quick.setText("Open")
        button_quick.setMaximumWidth(50)
        button_quick.clicked.connect(self._open_spellcheck)

        tab_spell.addWidget(label_spell, alignment=Qt.AlignHCenter)
        tab_spell.addWidget(button_quick, alignment=Qt.AlignHCenter)

        container_spell = DragNDropSpell()
        container_spell.setLayout(tab_spell)

        """ Dictionary Tab """
        tab_dict = QVBoxLayout()

        # Available dictionaries
        container_dict_avail = QVBoxLayout()

        # Available dictionaries - label
        label_dict_avail = QLabel()
        label_dict_avail.setText("Available dictionaries:")
        container_dict_avail.addWidget(label_dict_avail)

        # Available dictionaries - interactive container
        container_dict_avail_interactive = QHBoxLayout()

        # Available dictionaries - interactive container - list
        list_dict_avail = QListWidget()
        list_dict_avail.addItems(self._get_dictionary_items(DictionaryType.AVAILABLE))
        list_dict_avail.setObjectName('ListDictAvail')
        list_dict_avail.setSelectionMode(QAbstractItemView.ExtendedSelection)
        container_dict_avail_interactive.addWidget(list_dict_avail)

        container_dict_avail.addLayout(container_dict_avail_interactive)

        # Available dictionaries - buttons container
        container_dict_avail_buttons = QVBoxLayout()
        container_dict_avail_buttons.setAlignment(Qt.AlignTop)
        for button in self._make_buttons(DictionaryType.AVAILABLE):
            container_dict_avail_buttons.addWidget(button)
        container_dict_avail_interactive.addLayout(container_dict_avail_buttons)

        tab_dict.addLayout(container_dict_avail)

        # Loaded dictionaries
        container_dict_load = QVBoxLayout()

        # Loaded dictionaries - label
        label_dict_load = QLabel()
        label_dict_load.setText("Loaded dictionaries:")
        container_dict_load.addWidget(label_dict_load)

        # Loaded dictionaries - interactive container
        container_dict_load_interactive = QHBoxLayout()

        # Loaded dictionaries - interactive container - list
        list_dict_load = QListWidget()
        list_dict_load.addItems(self._get_dictionary_items(DictionaryType.LOADED))
        list_dict_load.setObjectName('ListDictLoad')
        list_dict_load.setSelectionMode(QAbstractItemView.ExtendedSelection)
        container_dict_load_interactive.addWidget(list_dict_load)

        container_dict_load.addLayout(container_dict_load_interactive)

        # Loaded dictionaries - buttons container
        container_dict_load_buttons = QVBoxLayout()
        container_dict_load_buttons.setAlignment(Qt.AlignTop)

        for button in self._make_buttons(DictionaryType.LOADED):
            container_dict_load_buttons.addWidget(button)
        container_dict_load_interactive.addLayout(container_dict_load_buttons)

        tab_dict.addLayout(container_dict_load)

        # Make layout into Widget
        container_dict = QWidget()
        container_dict.setLayout(tab_dict)

        # Add Tabs to UI
        tabs.addTab(container_quick, "Quick Run")
        tabs.addTab(container_scan, "Scan")
        tabs.addTab(container_spell, "Spellcheck")
        tabs.addTab(container_dict, "Dictionary")

        self.setCentralWidget(tabs)

        return

    def _open_dictionary_avail(self) -> None:
        dict_list = self.findChild(QListWidget, 'ListDictAvail')
        dictionary = dict_list.selectedItems()
        for item in dictionary:
            filepath = os.path.join('//resources', item.text())
            QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))

        return

    def _open_dictionary_load(self) -> None:
        dict_list = self.findChild(QListWidget, 'ListDictLoad')
        dictionary = dict_list.selectedItems()
        for item in dictionary:
            filepath = os.path.join('//dictionaries', item.text())
            QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))

        return

    def _add_dictionary(self) -> None:
        refresh: bool
        response: QMessageBox
        extant_resources: list[str]
        dst: Path

        refresh = False
        dst = Path('//resources')  # TODO: change this
        extant_resources = os.listdir(dst)

        files, _ = QFileDialog.getOpenFileNames(
            self,
            'Open',
            '',
            'All files (*.txt);;Text (*.txt)',
            options=QFileDialog.Options()
        )

        if files:
            for file in files:
                path = Path(file)
                if not is_filetype(path, ['.txt']):
                    error_dispatcher.raise_error("File Error", f"Warning: file type '{path.name}' not accepted.")
                else:
                    if path.name in extant_resources:
                        if QMessageBox.question(
                            self, 'Overwrite',
                            f"'{path.name}' already exists. Overwrite file?"
                        ) == QMessageBox.Yes:
                            copy(path, dst)
                            refresh = True
                    else:
                        copy(path, dst)
                        refresh = True

        if refresh:
            self._refresh_lists()

        return

    def _remove_dictionary(self) -> None:
        response: bool
        refresh: bool

        dict_list = self.findChild(QListWidget, 'ListDictAvail')
        dictionary = dict_list.selectedItems()

        if not dictionary:
            return

        refresh = False
        if QMessageBox.question(
            self, 'Confirm deletion',
            f"""You are about to delete {len(dictionary)} {'dictionary' if len(dictionary) < 2 else 'dictionaries'}.
            Are you sure?"""
        ) != QMessageBox.Yes:
            return

        for item in dictionary:
            filepath = Path('//resources', item.text())
            refresh = delete(filepath)

        if refresh:
            self._refresh_lists()

        return

    def _load_dictionary(self) -> None:
        src: Path
        dst: Path
        extant_dictionaries: list[str]

        src = Path('//resources')
        dst = Path('//dictionaries')

        dict_list = self.findChild(QListWidget, 'ListDictAvail')
        dictionary = dict_list.selectedItems()
        extant_dictionaries = os.listdir(dst)

        if not dictionary:
            return

        for item in dictionary:
            path = Path(item.text())
            if path.name in extant_dictionaries:
                if QMessageBox.question(
                        self, 'Overwrite',
                        f"'{path.name}' already exists. Overwrite file?"
                ) == QMessageBox.Yes:
                    filepath = Path(src, path)
                    move(filepath, dst, overwrite=True)
            else:
                filepath = Path(src, path)
                move(filepath, dst)

        self._refresh_lists()

        return

    def _unload_dictionary(self) -> None:
        src: Path
        dst: Path
        extant_resources: list[str]

        src = Path('//dictionaries')
        dst = Path('//resources')

        dict_list = self.findChild(QListWidget, 'ListDictLoad')
        dictionary = dict_list.selectedItems()
        extant_resources = os.listdir(dst)

        if not dictionary:
            return

        for item in dictionary:
            path = Path(item.text())
            if path.name in extant_resources:
                if QMessageBox.question(
                        self, 'Overwrite',
                        f"'{path.name}' already exists. Overwrite file?"
                ) == QMessageBox.Yes:
                    filepath = Path(src, path)
                    move(filepath, dst, overwrite=True)
            else:
                filepath = Path(src, item.text())
                move(filepath, dst, overwrite=True)

        self._refresh_lists()

        return

    def _refresh_lists(self) -> None:
        dict_list = self.findChild(QListWidget, 'ListDictAvail')
        dict_list.clear()
        dict_list.addItems(self._get_dictionary_items(DictionaryType.AVAILABLE))

        dict_list = self.findChild(QListWidget, 'ListDictLoad')
        dict_list.clear()
        dict_list.addItems(self._get_dictionary_items(DictionaryType.LOADED))

        return

    def _make_buttons(self, to_load: DictionaryType) -> list[QPushButton]:
        buttons: list[QPushButton]

        if to_load == DictionaryType.AVAILABLE:
            button_info = zip(
                ["Open", "New", "Remove", "Load"],
                [self._open_dictionary_avail, self._add_dictionary, self._remove_dictionary, self._load_dictionary]
            )
        else:
            button_info = zip(
                ["Open", "Unload"],
                [self._open_dictionary_load, self._unload_dictionary]
            )

        buttons = list()

        for text, func in button_info:
            button = QPushButton()
            button.setText(text)
            button.setMaximumWidth(60)
            button.clicked.connect(func)
            buttons.append(button)

        for button in buttons:
            yield button

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
        abs_path: Path
        path: Path

        abs_path = Path('/')
        path = Path(abs_path, 'resources' if to_load == DictionaryType.AVAILABLE else 'dictionaries')

        dictionaries = DirectoryContents([Path(path, item) for item in os.listdir(path)])  # TODO: fix this later
        dictionaries.clear_except('.txt')

        return [item.name for item in dictionaries]


def interface_init() -> None:
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()

    return


interface_init()
