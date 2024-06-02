from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QTabWidget, QLabel, QPushButton, QListWidget, QAbstractItemView
)
from PyQt5.QtCore import Qt

from .util import DragNDropAll, DragNDropScan, DragNDropSpell, DictionaryType


class TopBarTabs(QMainWindow):

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
        button_scan.clicked.connect(self._open_scan)

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
