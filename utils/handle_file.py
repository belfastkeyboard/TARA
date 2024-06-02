from pathlib import Path
from utils.system import is_filetype, is_directory, write, read, DirectoryContents
import os
from PIL import Image
from utils.error import error_dispatcher
from OCR import ocr
from spellcheck.spellcheck import Spellchecker
from utils.status import good
from utils.pdf import convert_pdf
from enum import Enum


class ProcessType(Enum):
    ALL = 0
    SCAN = 1
    SPELLCHECK = 2


def file_not_accepted(path: Path) -> None:
    error_dispatcher.raise_error("File Error", f"Warning: file type '{path.name}' not accepted.")


def file_process_image(path: Path, spellcheck: bool = True) -> None:
    image: Image
    text: str
    spellchecker: Spellchecker
    document: Path

    if not os.path.exists(path):
        error_dispatcher.raise_error("File not found", f"Warning: file {path.name} not found.")
        return

    text = ocr.get_text(path)

    if spellcheck:
        spellchecker = Spellchecker()
        text = spellchecker.spellcheck(text)

    document = Path(path.parent, f"{path.stem}.txt")
    write(text, document, 'w')
    good(f"Text saved as '{document.name}'.")

    return


def file_process_text(path: Path) -> None:
    text: list[str]
    spellchecker: Spellchecker
    document: Path

    if not os.path.exists(path):
        error_dispatcher.raise_error("File not found", f"Warning: file {path.name} not found.")
        return

    document = Path(path.parent, f"{path.stem}_spellchecked.txt")
    spellchecker = Spellchecker()

    text = read(path, True)
    text = spellchecker.spellcheck_batch(text)

    write(text, document, 'w')
    good(f"Text saved as '{document.name}'.")

    return


def file_process_document(path: Path, scan: bool = True, spellcheck: bool = True) -> None:
    images: DirectoryContents
    texts: list[str]
    spellchecker: Spellchecker
    doc: Path
    document: Path

    if not os.path.exists(path):
        error_dispatcher.raise_error("File not found", f"Warning: file {path.name} not found.")
        return

    images = convert_pdf(path)

    if scan:
        texts = ocr.get_text_batch(images)

        if spellcheck:
            spellchecker = Spellchecker()
            texts = spellchecker.spellcheck_batch(texts)

        document = Path(path.parent, f"{path.stem}.txt")
        write(texts, document, 'w')
        good(f"Text saved as '{document.name}'.")
    else:
        good(f"PDF processed, files saved in '{path.stem}'.")

    return


def file_handle_directory(path: Path, process: ProcessType = ProcessType.ALL) -> None:
    items: list[str]

    items = os.listdir(path)

    if not items:
        error_dispatcher.raise_error("Empty directory", f"Warning: '{str(path.stem)}' has no contents.")
        return

    for item in items:
        item = path.joinpath(path, item)

        if process == ProcessType.SCAN:
            discern_type_scan(item)
        elif process == ProcessType.SPELLCHECK:
            discern_type_spellcheck(item)
        else:
            discern_type_all(item)


def discern_type_all(path: Path) -> None:
    if is_filetype(path, ['.jpg', '.png']):
        file_process_image(path)
    elif is_filetype(path, ['.pdf']):
        file_process_document(path)
    elif is_filetype(path, ['.txt']):
        file_process_text(path)
    elif is_directory(path):
        file_handle_directory(path)
    else:
        file_not_accepted(path)


def discern_type_scan(path: Path) -> None:
    if is_filetype(path, ['.jpg', '.png']):
        file_process_image(path, spellcheck=False)  # TODO: scan only version (parameter?)
    elif is_filetype(path, ['.pdf']):
        file_process_document(path, spellcheck=False)  # TODO: scan only version (parameter?)
    elif is_directory(path):
        file_handle_directory(path, ProcessType.SCAN)  # TODO: scan only version (parameter?)
    else:
        file_not_accepted(path)


def discern_type_spellcheck(path: Path) -> None:
    if is_filetype(path, ['.txt']):
        file_process_text(path)
    elif is_directory(path):
        file_handle_directory(path, ProcessType.SPELLCHECK)
    else:
        file_not_accepted(path)
