import time
import concurrent.futures
from math import ceil
from pathlib import Path

import pytesseract as tesseract
from PIL import Image

from utils.status import good, info, progress, warn

from .flag import ScanFlags


class OCR:
    def __init__(self, files: list[Path], flags: ScanFlags, psm: int = 3):
        super().__init__()

        self.files = files
        self.flags = flags

        self.tesseract = tesseract
        self.psm = psm

        self.start_time = None
        self.end_time = None

        self.file_count = len(files)
        self.scanned_texts = list()

        self.scan()

        if self.flags:
            self.post_process()

        return

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return

    def scan(self):
        info("Scanning.")
        self.start_time = time.time()

        for i, file in enumerate(self.files):
            try:
                image = Image.open(file)
            except FileNotFoundError as e:
                warn(e)
                info(f"Cannot find '{str(file)}'.")
                return

            text = self.tesseract.image_to_string(image=image, config=f"--psm {self.psm}")
            self.scanned_texts.append(text)

            progress(
                text=f"Pages scanned: {i + 1} of {self.file_count}.",
                end='' if i + 1 < self.file_count else '\r'
            )

        self.end_time = time.time()
        good(f"Scanned in {(self.end_time - self.start_time):.2f} seconds.\n")

        return

    def post_process(self):
        if self.flags & ScanFlags.SplitPage:
            self.scanned_texts = self.split_page(self.scanned_texts)
        if self.flags & ScanFlags.FixHyphenation:
            self.scanned_texts = self.fix_hyphenation(self.scanned_texts)
        if self.flags & ScanFlags.FixNewlines:
            self.scanned_texts = self.fix_newlines(self.scanned_texts)

        return

    def get_text(self) -> list[str]:
        return self.scanned_texts

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
