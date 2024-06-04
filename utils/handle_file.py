import os
from enum import Enum
from pathlib import Path

from PIL import Image
from OCR import OCR
from spellcheck import Spellchecker

from utils.error import error_dispatcher
from utils.pdf import convert_pdf
from utils.status import good
from utils.system import DirectoryContents, is_directory, is_filetype, read, write


class ProcessType(Enum):
    ALL = 0
    SCAN = 1
    SPELLCHECK = 2


def file_not_accepted(path: Path) -> None:
    error_dispatcher.raise_error("File Error", f"Warning: file type '{path.name}' not accepted.")


def file_process_image(path: Path, spellcheck: bool = True) -> None:
    text: str
    document: Path

    if not os.path.exists(path):
        error_dispatcher.raise_error("File not found", f"Warning: file {path.name} not found.")
        return

    with OCR() as ocr:
        text = ocr.get_text([path])[0]

    if spellcheck:
        with Spellchecker() as check:
            if not check.loaded:
                error_dispatcher.raise_error(
                    "No dictionaries loaded!",
                    "No dictionaries have been loaded.\nUse the 'Dictionary' tab to load dictionaries."
                )
            else:
                text = check.spellcheck(text)

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

    text = read(path, True)
    with Spellchecker() as check:
        if not check.loaded:
            error_dispatcher.raise_error(
                "No dictionaries loaded!",
                "No dictionaries have been loaded.\nUse the 'Dictionary' tab to load dictionaries."
            )
        else:
            text = check.spellcheck_batch(text)

    document = Path(path.parent, f"{path.stem}_spellchecked.txt")
    write(text, document, 'w')
    good(f"Text saved as '{document.name}'.")

    return


def file_process_document(path: Path, scan: bool = True, spellcheck: bool = True) -> None:
    images: DirectoryContents
    texts: list[str]
    doc: Path
    document: Path

    if not os.path.exists(path):
        error_dispatcher.raise_error("File not found", f"Warning: file {path.name} not found.")
        return

    images = convert_pdf(path)

    if scan:
        with OCR() as ocr:
            texts = ocr.get_text(images)

        document = Path(path.parent, path.stem, f"{path.stem}.txt")
        write('\n'.join(texts), document, 'w')

        if spellcheck:
            with Spellchecker() as check:
                if not check.loaded:
                    error_dispatcher.raise_error(
                        "No dictionaries loaded!",
                        "No dictionaries have been loaded.\nUse the 'Dictionary' tab to load dictionaries."
                    )
                else:
                    texts = check.spellcheck_batch(texts)

        document = Path(path.parent, path.stem, f"{path.stem} spellchecked.txt")
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
        file_process_image(path, spellcheck=False)
    elif is_filetype(path, ['.pdf']):
        file_process_document(path, spellcheck=False)
    elif is_directory(path):
        file_handle_directory(path, ProcessType.SCAN)
    else:
        file_not_accepted(path)


def discern_type_spellcheck(path: Path) -> None:
    if is_filetype(path, ['.txt']):
        file_process_text(path)
    elif is_directory(path):
        file_handle_directory(path, ProcessType.SPELLCHECK)
    else:
        file_not_accepted(path)
