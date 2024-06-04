import time
from pathlib import Path

import pytesseract as tesseract
from PIL import Image

from utils.status import good, info, progress, warn


class OCR:
    def __init__(self, psm: int = 3, split_page: bool = True, fix_hyphenation: bool = True, fix_newline: bool = True):
        super().__init__()

        self.tesseract = tesseract

        self.psm = psm
        self.page = split_page
        self.hyphenation = fix_hyphenation
        self.newlines = fix_newline

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return

    def get_text(self, files: list[Path], log: bool = True) -> list[str]:
        scanned_texts: list[str]

        scanned_texts = list()
        start = time.time()
        file_count = len(files)

        if log:
            info("Scanning.")

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

            scanned_texts.append(self.tesseract.image_to_string(image=image, config=f"--psm {self.psm}"))

        end = time.time()

        if log:
            good(f"Scanned in {(end - start):.2f} seconds.\n")

        if self.page:
            scanned_texts = self.split_page(scanned_texts)
        if self.hyphenation:
            scanned_texts = self.fix_hyphenation(scanned_texts)
        if self.newlines:
            scanned_texts = self.fix_newlines(scanned_texts)  # TODO: move this block into the object itself

        return scanned_texts

    @staticmethod
    def split_page(pages: list[str]) -> list[str]:
        split_pages = [page.split('\n\n') for page in pages]
        return [line for sublist in split_pages for line in sublist]

    @staticmethod
    def fix_hyphenation(paragraphs: list[str]) -> list[str]:
        return [paragraph.replace('-\n', '') for paragraph in paragraphs]

    @staticmethod
    def fix_newlines(paragraphs: list[str]) -> list[str]:
        return [paragraph.replace('\n', ' ') for paragraph in paragraphs]
