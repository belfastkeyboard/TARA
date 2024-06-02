from PyQt5.QtWidgets import QMainWindow, QMenu, QAction, QStyle


class TopBarMenu(QMainWindow):
    def _create_menu(self) -> None:
        menu = self.menuBar()

        m_file = QMenu('&File', self)
        m_file.setFixedWidth(80)
        menu.addMenu(m_file)

        m_open_all = QAction('&Open', self)
        m_open_all.setShortcut('Ctrl+O')
        m_open_all.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        m_open_all.triggered.connect(self._open_file)
        m_file.addAction(m_open_all)

        m_help = QMenu('&Help', self)
        m_help.setFixedWidth(95)
        menu.addMenu(m_help)

        m_open_help = QAction('How to...', self)
        m_open_help.setIcon(self.style().standardIcon(QStyle.SP_DialogHelpButton))
        m_open_help.triggered.connect(self._open_help)
        m_help.addAction(m_open_help)

        return
