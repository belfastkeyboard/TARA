import os
import time
from pathlib import Path
from sys import exit

import pdf2image
from pdf2image.exceptions import PDFPopplerTimeoutError
from PIL import Image

from utils.exception import FileTypeError
from utils.status import good, info, progress, warn
from utils.system import is_filetype, copy, create_new_directory, DirectoryContents


def convert_pdf(pdf: Path) -> DirectoryContents:
    images: DirectoryContents
    directory: Path
    img_directory: Path

    try:
        if not os.path.exists(pdf):
            raise FileNotFoundError(f"File '{pdf}' not found.")
        elif is_filetype(pdf, ['.jpg']):
            raise FileTypeError(pdf.suffix)
    except (FileNotFoundError, FileTypeError) as e:
        warn(e)
        exit(1)

    directory = Path(pdf.parent, pdf.stem)
    img_directory = Path(directory, 'images')

    create_new_directory(directory)
    create_new_directory(img_directory)

    images = DirectoryContents(_create_jpgs_from_pdf(pdf, img_directory))
    copy(pdf, directory)

    images.sort()

    return images


# TODO: multithread this, I/O operation, can probably almost x4 this operation
#   use range to determine where to start, and increment in 4s?
#   i.e. start 1-4 (skip 4 * 3) 16-20, etc.
def _create_jpgs_from_pdf(pdf: Path, directory: Path) -> list[Path]:
    batch_size: int
    page_count: int
    total_pages: int

    batch_size = 1
    total_pages = _get_pdf_page_count(pdf)

    info("Converting .pdf to .jpgs.")
    start = time.time()

    try:
        for start_page in range(1, total_pages + 1, batch_size):
            end_page = min(start_page + (batch_size - 1), total_pages)
            images = pdf2image.convert_from_path(pdf_path=pdf, timeout=20, first_page=start_page, last_page=end_page)
            _save_images(images, directory, start_page)
            del images
            progress(
                text=f"Pages converted: {start_page} of {total_pages}.", end='' if start_page < total_pages else '\r'
            )
    except PDFPopplerTimeoutError as e:
        warn(e)
        exit(1)

    end = time.time()
    good(f"Conversion completed in {(end - start):.2f}.\n")

    return [Path(directory, item) for item in os.listdir(directory)]


def _save_images(images: list[Image], directory: Path, start_page: int) -> None:
    for x, image in enumerate(images, start_page):
        image.save(f"{str(directory)}/{x}_a.jpg", "JPEG")

    return


def _get_pdf_page_count(pdf: Path) -> int:
    return pdf2image.pdfinfo_from_path(str(pdf))['Pages']
