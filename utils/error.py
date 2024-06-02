from PyQt5.QtCore import QObject, pyqtSignal


class ErrorMessage(QObject):
    error = pyqtSignal(str, str)

    def raise_error(self, title: str, message: str):
        self.error.emit(title, message)  # this is a static analysis problem, doesn't affect runtime


error_dispatcher = ErrorMessage()
