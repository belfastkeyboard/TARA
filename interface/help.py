from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QDialog, QTextBrowser, QVBoxLayout


class HelpWindow(QDialog):

    def __init__(self):
        super().__init__()

        self.setFixedSize(QSize(400, 320))
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.setWindowTitle('Help')

        layout = QVBoxLayout()

        text_edit = QTextBrowser()
        text_edit.setHtml("""
            <h1 style="text-align: center;">Help</h1>
            <h2>Quick Run</h2>
            <p>Use by default for most operations.</p>
            <p>Quick Run will automatically process any valid files [*.jpg, *.png, *.pdf, *.txt] given to it.</p>
            <p>If passed an image or PDF file, it will scan, spellcheck, and save.</p>
            <p>If passed a .txt file it will spellcheck and save.</p>
            <p>In order to spellcheck, at least one dictionary must be provided in the 'Dictionary' tab.</p>
            <h2>Scan</h2>
            <p>Scan will scan any valid files [*.jpg, *.png, *.pdf] and save to .txt.</p>
            <p>It will not spellcheck the text.</p>
            <h2>Spellcheck</h2>
            <p>Spellcheck will spellcheck any .txt file given to it and save as a new '*_checked.txt' file.</p>
            <p>In order to spellcheck, at least one dictionary must be provided in the 'Dictionary' tab.</p>
            <h2>Dictionary</h2>
            <p>The Dictionary tab allows for handling dictionaries.</p>
            <p>It maintains two lists of dictionaries:</p>
            <ol>
            <li>
            <p>Available dictionaries</p>
            </li>
            <li>
            <p>Loaded dictionaries</p>
            </li>
            </ol>
            <p>All commands work on single and multiple dictionary files.</p>
            <h3>Available dictionaries</h3>
            <p><strong>Open:</strong> Opens selected dictionary in default .txt editor.</p>
            <p><strong>New:</strong> Add a new dictionary to <em>Available Dictionaries</em>.</p>
            <p><strong>Remove:</strong> Deletes the dictionary.</p>
            <p><strong>Load:</strong> Loads the dictionary into <em>Loaded Dictionaries</em>.</p>
            <h3>Loaded dictionaries</h3>
            <p><strong>Open:</strong> Opens selected dictionary in default .txt editor.</p>
            <p><strong>Unload:</strong> Unloads the dictionary and sends back to <em>Available Dictionaries</em>.</p>
        """)
        layout.addWidget(text_edit)

        self.setLayout(layout)
