import os
import shutil
from pathlib import Path, PosixPath
from utils.status import warn, info
import re
from utils.error import error_dispatcher


class DirectoryContents(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def sort(self, key=None, reverse=False):
        super().sort(key=self._extract_number, reverse=reverse)

    @staticmethod
    def _extract_number(filename: PosixPath) -> int:
        match = re.search(r'(\d+)', filename.name)
        return int(match.group(1)) if match else 0

    def clear_except(self, exception: str) -> None:
        file_type: str
        exceptions: list[PosixPath]

        exceptions = list()

        for element in self:
            try:
                if not isinstance(element, PosixPath):
                    raise TypeError("Non-path encountered in clear_except().")
            except TypeError as e:
                warn(e)

            if element.suffix == exception:
                exceptions.append(element)

        self.clear()
        self.extend(exceptions)


def clear_dir(directory: Path) -> None:

    for file in os.listdir(directory):
        path = Path(os.path.join(directory, file))
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            clear_dir(path)
            os.rmdir(path)


def clear_dir_by_filetype(directory: Path, extension: str) -> None:
    for file in os.listdir(directory):
        path = Path(os.path.join(directory, file))
        if os.path.isfile(path) and os.path.splitext(path)[1] == extension:
            os.remove(path)
        elif os.path.isdir(path):
            clear_dir_by_filetype(path, extension)

    return


def copy(src: Path, dst: Path) -> Path:
    return Path(shutil.copy2(src, dst))


# TODO: implement return value if dst contains same filename?
def move(src: Path, dst: Path, overwrite: bool = False) -> bool:
    try:
        shutil.move(src, dst)
    except shutil.Error:
        if overwrite:
            os.remove(Path(dst, src.name))
            shutil.move(src, dst)
        else:
            return False
    return True


def delete(path: Path) -> bool:
    try:
        os.remove(path)
    except FileNotFoundError as e:
        warn(e)
        info(f"Path: {str(path)}.")
    finally:
        return not os.path.exists(path)


def read(path: Path, multi: bool) -> list[str] | str:
    with open(path, 'r') as f:
        return f.readlines() if multi else f.read()


def write(content: str | list[str], path: Path, mode: str) -> None:
    with open(path, mode) as f:
        f.write(content) if isinstance(content, str) else f.writelines(content)


def create_new_directory(directory: Path) -> None:
    if not os.path.exists(directory):
        os.mkdir(directory)

    if not os.path.exists(directory):
        error_dispatcher.raise_error("System Error", f"Failed to create directory '{str(directory.name)}'.")
        return

    if os.listdir(directory):
        clear_dir(directory)

    return


def get_file_type(path: Path) -> str:
    return path.suffix


def is_filetype(path: Path, filetypes: list[str]) -> bool:
    return path.suffix in filetypes


def is_directory(path: Path) -> bool:
    return path.is_dir()
