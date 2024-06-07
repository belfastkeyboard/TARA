import re
import time
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
        texts = self.split_page(self.scanned_texts)
        texts = self.fix_hyphenation(texts)
        texts = self.fix_newlines(texts)
        texts = self.fix_pre_punctuation_space(texts)
        texts = self.fix_post_punctuation_space(texts)

        self.scanned_texts = texts

        return

    def get_text(self) -> list[str]:
        return self.scanned_texts

    @staticmethod
    def split_page(text: list[str]) -> list[str]:
        split_pages = [page.split('\n\n') for page in text]
        return [page for pages in split_pages for page in pages]

    @staticmethod
    def fix_hyphenation(paragraphs: list[str]) -> list[str]:
        return [paragraph.replace('-\n', '') for paragraph in paragraphs]

    @staticmethod
    def fix_newlines(paragraphs: list[str]) -> list[str]:
        return [paragraph.replace('\n', ' ') for paragraph in paragraphs]

    @staticmethod
    def fix_pre_punctuation_space(paragraphs: list[str]) -> list[str]:
        return [re.sub(r'\b ([”;])', r'\1', paragraph) for paragraph in paragraphs]

    @staticmethod
    def fix_post_punctuation_space(paragraphs: list[str]) -> list[str]:
        return [re.sub(r'“ \b', r'“', paragraph) for paragraph in paragraphs]
