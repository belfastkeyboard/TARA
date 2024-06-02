from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox

from pathlib import Path
from utils.handle_file import discern_type_all, discern_type_scan, discern_type_spellcheck
from utils.error import error_dispatcher
from .help import HelpWindow


class Processes(QMainWindow):

    def __init__(self):
        super().__init__()
        self.help = None

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
                if not discern_type_all(path):
                    error_dispatcher.raise_error()  # what's going on with this syntax?

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

    def _open_help(self) -> None:
        self.help = HelpWindow()
        self.help.exec()
