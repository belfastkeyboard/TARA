import os
import re
from pathlib import Path
from sys import exit

import pytesseract
from PIL import Image

from utils.exception import EmptyDirectoryError
from utils.status import warn
from utils.system import DirectoryContents

# TODO: add docx functionality


def read_chars(directory: str) -> list[str]:
    page_text: str
    pages: list[str]
    dir_contents: DirectoryContents

    try:
        if not os.path.isdir(directory):
            raise NotADirectoryError(f"The path '{directory}' does not point to a valid directory.")
        elif not os.listdir(directory):
            raise EmptyDirectoryError(directory)
    except (NotADirectoryError, EmptyDirectoryError) as e:
        warn(e)
        exit(1)

    dir_contents = DirectoryContents(os.listdir(directory))
    dir_contents.sort()
    dir_contents.clear_except('.jpg')
    pages = list()

    for page in dir_contents:
        page = Path(directory, page)
        page_text = pytesseract.image_to_string(Image.open(page))
        pages.append(page_text)

    return pages


def write_chars(pages: list[str], save_path: str) -> None:
    paragraphs: list[str]
    document: Document

    document = Document()

    for page in pages:
        paragraphs = split_page_into_paragraphs(page)
        paragraphs = sanitise_paragraphs(paragraphs)

        for paragraph in paragraphs:
            document.add_paragraph(paragraph)

        document.add_page_break()

    document.save(f"{save_path}.docx")

    return


def split_page_into_paragraphs(page: str) -> list[str]:
    paragraphs: list[str]

    paragraphs = page.split('\n\n')

    return paragraphs


def turn_newlines_into_spaces(paragraph: str) -> str:
    return paragraph.replace('\n', ' ')


def fix_hyphenation(paragraph: str) -> str:
    return re.sub(r'- [a-zA-Z]', '', paragraph)


def sanitise_paragraphs(paragraphs: list[str]) -> list[str]:
    sanitised_paragraphs: list[str]

    sanitised_paragraphs = list()

    for paragraph in paragraphs:
        paragraph = turn_newlines_into_spaces(paragraph)
        sanitised_paragraphs.append(paragraph)

    return sanitised_paragraphs
