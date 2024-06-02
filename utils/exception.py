class EmptyDirectoryError(Exception):
    """Throw when the directory is unexpectedly empty"""

    def __init__(self, directory):
        self.message = f"The directory '{directory}' is empty."
        super().__init__(self.message)


class FileTypeError(Exception):
    """Throw when unexpected filetpye is encountered"""

    def __init__(self, filetype):
        self.message = f"Unexpected file type: '{filetype}'."
        super().__init__(self.message)
