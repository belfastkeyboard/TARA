from PyQt5.QtWidgets import QMainWindow, QPushButton, QListWidget, QMessageBox, QFileDialog
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices

from pathlib import Path
import os
from utils.system import move, delete, copy, is_filetype
from utils.error import error_dispatcher

from .util import DictionaryType

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
RESOURCES_DIR = Path(PROJECT_DIR, 'resources')
DICTIONARY_DIR = Path(PROJECT_DIR, 'dictionaries')


class DictionaryMethods(QMainWindow):

    def _open_dictionary_avail(self) -> None:
        dict_list = self.findChild(QListWidget, 'ListDictAvail')
        dictionary = dict_list.selectedItems()

        for item in dictionary:
            filepath = os.path.join(RESOURCES_DIR, item.text())
            QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))

        return

    def _open_dictionary_load(self) -> None:
        dict_list = self.findChild(QListWidget, 'ListDictLoad')
        dictionary = dict_list.selectedItems()

        for item in dictionary:
            filepath = os.path.join(DICTIONARY_DIR, item.text())
            QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))

        return

    def _add_dictionary(self) -> None:
        refresh: bool
        response: QMessageBox
        extant_resources: list[str]

        refresh = False
        extant_resources = os.listdir(RESOURCES_DIR)

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
                            copy(path, RESOURCES_DIR)
                            refresh = True
                    else:
                        copy(path, RESOURCES_DIR)
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
            filepath = Path(RESOURCES_DIR, item.text())
            refresh = delete(filepath)

        if refresh:
            self._refresh_lists()

        return

    def _load_dictionary(self) -> None:
        extant_dictionaries: list[str]

        dict_list = self.findChild(QListWidget, 'ListDictAvail')
        dictionary = dict_list.selectedItems()
        extant_dictionaries = os.listdir(DICTIONARY_DIR)

        if not dictionary:
            return

        for item in dictionary:
            path = Path(item.text())
            if path.name in extant_dictionaries:
                if QMessageBox.question(
                        self, 'Overwrite',
                        f"'{path.name}' already exists. Overwrite file?"
                ) == QMessageBox.Yes:
                    filepath = Path(RESOURCES_DIR, path)
                    move(filepath, DICTIONARY_DIR, overwrite=True)
            else:
                filepath = Path(RESOURCES_DIR, path)
                move(filepath, DICTIONARY_DIR)

        self._refresh_lists()

        return

    def _unload_dictionary(self) -> None:
        extant_resources: list[str]

        dict_list = self.findChild(QListWidget, 'ListDictLoad')
        dictionary = dict_list.selectedItems()
        extant_resources = os.listdir(RESOURCES_DIR)

        if not dictionary:
            return

        for item in dictionary:
            path = Path(item.text())
            if path.name in extant_resources:
                if QMessageBox.question(
                        self, 'Overwrite',
                        f"'{path.name}' already exists. Overwrite file?"
                ) == QMessageBox.Yes:
                    filepath = Path(DICTIONARY_DIR, path)
                    move(filepath, RESOURCES_DIR, overwrite=True)
            else:
                filepath = Path(DICTIONARY_DIR, item.text())
                move(filepath, RESOURCES_DIR, overwrite=True)

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
