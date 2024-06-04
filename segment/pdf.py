import os
import time
import threading
from math import ceil
from pathlib import Path
from threading import Thread

import pdf2image as pdf2img
from PIL import Image

from utils.error import error_dispatcher
from utils.exception import FileTypeError
from utils.status import good, info, progress, warn
from utils.system import is_filetype, copy, create_new_directory, DirectoryContents


class Segment:
    def __init__(self, pdf: Path) -> None:
        self.pdf_path = pdf
        self.work_dir = Path(self.pdf_path.parent, self.pdf_path.stem)
        self.img_dir = Path(self.work_dir, 'images')
        self.page_count = self.count_page()

        try:
            if not os.path.exists(self.pdf_path):
                raise FileNotFoundError(f"File '{self.pdf_path.name}' not found.")
            elif not is_filetype(self.pdf_path, ['.pdf']):
                raise FileTypeError(self.pdf_path.suffix)
        except (FileNotFoundError, FileTypeError) as e:
            warn(e)
            return

        self.start_time = None
        self.end_time = None

        self.create_work_directories()
        self.segment()

        return

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type:
            error_dispatcher.raise_error(f"{exc_val}", f"Traceback: {exc_tb}.")
            return True

        return False

    def create_work_directories(self) -> None:
        create_new_directory(self.work_dir)
        copy(self.pdf_path, self.work_dir)

        create_new_directory(self.img_dir)

        return

    def segment(self):
        threads: list[Thread]
        batch: int

        threads = list()
        batch = ceil(self.page_count / 4)

        info("Converting .pdf to .jpgs.")
        self.start_time = time.time()

        for i in range(1, self.page_count + 1, batch):
            begin = i
            end = min(i + batch, self.page_count + 1)

            thread = threading.Thread(target=self.thread_segment, args=(begin, end))
            threads.append(thread)
            thread.start()

        while len(os.listdir(self.img_dir)) < self.page_count:
            progress(
                text=f"Pages converted: {len(os.listdir(self.img_dir))} of {self.page_count}.",
                end='' if len(os.listdir(self.img_dir)) < self.page_count else '\r'
            )

        for thread in threads:
            thread.join()

        self.end_time = time.time()
        good(f"Conversion completed in {(self.end_time - self.start_time):.2f}.\n")

        return

    def thread_segment(self, begin: int, end: int):
        for page in range(begin, end):
            image = pdf2img.convert_from_path(
                pdf_path=self.pdf_path, timeout=20, first_page=page, last_page=page+1
            )
            self.save_image(image[0], page)

        return

    def get_result(self) -> DirectoryContents:
        images = DirectoryContents([Path(self.img_dir, image) for image in os.listdir(self.img_dir)])
        images.sort()

        return images

    def save_image(self, image: Image, i: int) -> None:
        path = Path(self.img_dir, f"{i}.jpg")
        image.save(path, 'JPEG')

        return

    def count_page(self) -> int:
        return pdf2img.pdfinfo_from_path(str(self.pdf_path))['Pages']
