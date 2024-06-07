import re
import time
from pathlib import Path
from typing import Sequence

import cv2
import numpy as np
import pytesseract as tesseract
from numpy import ndarray as image

from preprocess.helper import ImgManipFlags, BoundingBox
from utils.status import info, good, progress

""" if this isn't included there is a fatal import error """
import os
import sys
ci_build_and_not_headless = False
try:
    from cv2.version import ci_build, headless
    ci_and_not_headless = ci_build and not headless
except:
    pass
if sys.platform.startswith("linux") and ci_and_not_headless:
    os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH")
if sys.platform.startswith("linux") and ci_and_not_headless:
    os.environ.pop("QT_QPA_FONTDIR")
""" end of """


class ImageProcessing:
    def __init__(self, files: list[Path], flags: ImgManipFlags):
        self.files = files
        self.images = list()

        self.flags = flags
        self.image_count = len(self.files)

        self.start = None
        self.end = None

        return

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return

    def process(self):
        assert self.files, "No files in ImageProcessing.files"

        info(f"Processing image{'s' if len(self.images) > 1 else ''}.")
        self.start = time.time()

        for i, file in enumerate(self.files):
            img = cv2.imread(str(file))

            if self.flags & ImgManipFlags.ResizeImage:
                img = self.resize(img)

            edit_img = self.get_edges(img)
            contours = self.get_contours(edit_img)
            bounding = self.get_likely_components(contours)

            if not bounding:
                progress(
                    text=f"Images processed: {i + 1}  out of {self.image_count}.",
                    end='' if i + 1 < self.image_count else '\r'
                )
                continue

            if self.flags & ImgManipFlags.CropRunningHeader:
                bounding = self.crop_running_header(img, bounding)
            if self.flags & ImgManipFlags.CropPageNumber:
                bounding = self.crop_page_number(img, bounding)

            region = self.get_text_region(bounding)

            img = img[region.y:region.y + region.h, region.x:region.x + region.w]
            self.save_image(file, img)

            progress(
                text=f"Images processed: {i + 1}  out of {self.image_count}.",
                end='' if i + 1 < self.image_count else '\r'
             )

        self.end = time.time()
        good(f"Image processing complete in {self.end - self.start} seconds.\n")

        return

    @staticmethod
    def get_edges(img: image) -> image:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.bilateralFilter(gray, 9, 75, 75)
        edges = cv2.Canny(blur, 200, 150)

        return edges

    @staticmethod
    def get_contours(img: image, draw: bool = False, tuning: int = 15) -> Sequence[image]:
        _, threshold = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel = np.ones((tuning, tuning), np.uint8)
        dilate = cv2.dilate(threshold, kernel, iterations=1)
        contours, _ = cv2.findContours(dilate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if draw:
            cv2.drawContours(dilate, contours, -1, (255, 255, 255), 2)

        return contours

    @staticmethod
    def get_likely_components(contours: Sequence[image], draw: bool = False, img: image = None) -> list[BoundingBox]:
        bounding = [BoundingBox(tuple(cv2.boundingRect(contour))) for contour in contours]
        bounding = [box for box in bounding if not (box.h / box.w > 0.8 and box.size() < 1000)]  # TODO: this was 1000

        if draw:
            for bound in bounding:
                cv2.rectangle(img, (bound.x, bound.y), (bound.x + bound.w, bound.y + bound.h), (255, 255, 255), 2)

        return bounding

    @staticmethod
    def crop_running_header(img: image, bounding: list[BoundingBox]) -> list[BoundingBox]:
        img_height = img.shape[0]
        img_width = img.shape[1]
        top_margin = img_height * 0.1  # TODO: make this a configurable value

        threshold = 0

        sorted_bounding = list(filter(lambda b: b.y < top_margin, bounding))
        sorted_bounding = sorted(sorted_bounding, key=lambda b: b.y)

        for box in sorted_bounding:
            if box.y < top_margin and box.h / box.w < 0.3:
                y1 = max(0, box.y - 3)
                y2 = min(box.y + box.h + 3, img_height)
                x1 = max(0, box.x - 3)
                x2 = min(box.x + box.w + 3, img_width)

                aoi = img[y1:y2, x1:x2]
                is_header: str = tesseract.image_to_string(aoi)
                is_header = re.sub(r'[^a-zA-Z0-9]', r'', is_header)

                if is_header and is_header.isalpha():
                    threshold = y2
                    break

        return [box for box in bounding if box.y > threshold]

    @staticmethod
    def crop_page_number(img: image, bounding: list[BoundingBox]) -> list[BoundingBox]:
        img_height = img.shape[0]
        img_width = img.shape[1]
        top_margin = img_height * 0.9  # TODO: make this a configurable value

        threshold = img_height

        sorted_bounding = list(filter(lambda b: b.y > top_margin, bounding))
        sorted_bounding = sorted(sorted_bounding, key=lambda b: b.y, reverse=True)

        for box in sorted_bounding:
            if box.y > top_margin and box.h / box.w > 0.7:
                y1 = max(0, box.y - 3)
                y2 = min(box.y + box.h + 3, img_height)
                x1 = max(0, box.x - 3)
                x2 = min(box.x + box.w + 3, img_width)

                aoi = img[y1:y2, x1:x2]
                is_header: str = tesseract.image_to_string(aoi)
                is_header = re.sub(r'[^a-zA-Z0-9]', r'', is_header)

                if is_header and is_header.isalpha():
                    threshold = y2
                    break

        return [box for box in bounding if box.y > threshold]

    @staticmethod
    def get_text_region(bounding: list[BoundingBox]) -> BoundingBox:
        all_x = [box.x for box in bounding]
        all_y = [box.y for box in bounding]
        all_w = [box.w for box in bounding]
        all_h = [box.h for box in bounding]

        x = min(all_x)
        y = min(all_y)
        w = max(x + w for x, w in zip(all_x, all_w))
        h = max(y + h for y, h in zip(all_y, all_h))

        return BoundingBox((x, y, w - x, h - y))

    # this method currently makes tesseract less accurate by resizing
    @staticmethod
    def resize(img: image, w: int = 6, h: int = 9) -> image:
        # width = w * 200
        # height = h * 200

        # img_width = img.shape[0]
        # img_height = img.shape[1]

        resize = img

        # if img_width < width or img_height < height:
        #     resize = cv2.resize(img, (width, height), interpolation=cv2.INTER_LINEAR)

        return resize

    @staticmethod
    def save_image(file: Path, img: image):
        cv2.imwrite(f"{str(file)}", img)
