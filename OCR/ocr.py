import time
from pathlib import Path

from PIL import Image
import pytesseract

from utils.status import warn, info, good, progress


def get_text(file: Path, log: bool = True) -> str:
    """
    Get character data from a single image.

    Parameters
    ----------
    file
        Path object pointing to directory of image to read.
    log
        Log activity to console. Default false.


    Returns
    -------
    Pages:
       List of pages, each page is a string.
    """
    if log:
        info(f"Scanning '{file.name}'.")

    start = time.time()

    try:
        image = Image.open(file)
    except FileNotFoundError as e:
        warn(e)
        info(f"Cannot find file at '{file}'.")
        exit(1)

    end = time.time()

    if log:
        good(f"Scanned in {(end - start):.2f} seconds.")

    return pytesseract.image_to_string(image)


def get_text_batch(files: list[Path], log: bool = True) -> list[str]:
    scanned_texts: list[str]

    scanned_texts = list()
    start = time.time()
    file_count = len(files)

    if log:
        info("Scanning images.")

    for i, file in enumerate(files):

        if log:
            progress(
                text=f"Scanning '{file.name}' {i + 1} out of {file_count}.",
                end='' if i + 1 < file_count else '\r'
            )

        try:
            image = Image.open(file)
        except FileNotFoundError as e:
            warn(e)
            info(f"Cannot find '{str(file)}'.")
            exit(1)

        scanned_texts.append(pytesseract.image_to_string(image))

    end = time.time()

    if log:
        good(f"Scanned in {(end - start):.2f} seconds.\n")

    return scanned_texts
