import re
import sys
from pathlib import Path

import cv2
import numpy as np
import pytesseract as tesseract
from PIL import Image

from preprocess.helper import ImgManipFlags, BoundingBox

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


# TODO: make ImageProcessing a bit more modular

# TODO: URGENT!!
#   the current process is not cropping correctly
#   revised idea
#   get edges, then get contours, then crop (in one method)
#   then get (will need to process edges and contours again but sure) bounding boxes and use to crop the header
#   this removes the number of necessary methods and should work better

class ImageProcessing:
    def __init__(self, files: list[Path], flags: ImgManipFlags):
        self.files = files
        self.images = list([cv2.imread(str(file)) for file in self.files])
        self.edited_images = list()
        self.contours = list()
        self.bounding_boxes = list()

        self.flags = flags

        self.crop()

        if self.flags & ImgManipFlags.CannyEdgeDetection:
            self.edge_detection()
        if self.flags & ImgManipFlags.ContourDetection:
            self.contour_detection()
        if self.flags & ImgManipFlags.BoundingBoxDetection:
            self.bounding_box_detection()
        if self.flags & ImgManipFlags.CropRunningHeader:
            self.crop_running_header()
        if self.flags & ImgManipFlags.CropBodyText:
            self.crop_body_text()

        return

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return

    def crop(self):
        assert self.images, "No images in ImageProcessing.images"

        for i, image in enumerate(self.images):
            # get edges
            edit_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # edit_img = cv2.medianBlur(edit_img, 3)
            edit_img = cv2.bilateralFilter(edit_img, 9, 75, 75)
            edit_img = cv2.Canny(edit_img, 200, 150)

            # get contours
            _, edit_img = cv2.threshold(edit_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            kernel = np.ones((15, 15), np.uint8)
            edit_img = cv2.dilate(edit_img, kernel, iterations=1)
            contours, _ = cv2.findContours(edit_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            bounding = [BoundingBox(tuple(cv2.boundingRect(contour))) for contour in contours]
            bounding = [box for box in bounding if not (box.h / box.w > 0.8 and box.size() < 1000)]

            if not bounding:
                continue

            # crop running header area
            # TODO: add if statement here
            img_height, img_width = image.shape[0], image.shape[1]
            top_margin = image.shape[0] * 0.1  # TODO: make this a configurable value
            threshold = 0
            bounding = sorted(bounding, key=lambda b: b.y)

            for box in bounding:
                if box.y < top_margin and box.h / box.w < 0.3:
                    y1 = max(0, box.y - 3)
                    y2 = min(box.y + box.h + 3, img_height)
                    x1 = max(0, box.x - 3)
                    x2 = min(box.x + box.w + 3, img_width)

                    aoi = image[y1:y2, x1:x2]
                    is_header: str = tesseract.image_to_string(aoi)
                    is_header = re.sub(r'[^a-zA-Z0-9]', r'', is_header)
                    if is_header and is_header.isalpha():
                        threshold = y2
                        break
            bounding = [box for box in bounding if box.y > threshold]

            # get text region
            all_x = [box.x for box in bounding]
            all_y = [box.y for box in bounding]
            all_w = [box.w for box in bounding]
            all_h = [box.h for box in bounding]

            x = min(all_x)
            y = min(all_y)
            w = max(x + w for x, w in zip(all_x, all_w))
            h = max(y + h for y, h in zip(all_y, all_h))
            text = BoundingBox((x, y, w - x, h - y))

            # crop page number area
            # TODO: add if statement here

            self.images[i] = image[text.y:text.y+text.h, text.x:text.x+text.w]

        return

    def edge_detection(self):
        assert self.images, "No images in ImageProcessing.images"

        for i, image in enumerate(self.images):
            if len(image.shape) != 2:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            image = cv2.Canny(image, 100, 200)
            self.edited_images.append(image)

        return

    def contour_detection(self):
        assert self.edited_images, "No edited images in ImageProcessing.edited_images"

        for i, image in enumerate(self.edited_images):
            if len(image.shape) != 2:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            _, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            kernel = np.ones((15, 15), np.uint8)
            image = cv2.dilate(image, kernel, iterations=1)
            contours, _ = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # cv2.drawContours(image, contours, -1, (0, 0, 255), 4)

            self.edited_images[i] = image
            self.contours.append(contours)

        return

    def bounding_box_detection(self):
        assert self.contours, "No contours in ImageProcessing.contours"

        for i, contours in enumerate(self.contours):
            boxes = []
            for contour in contours:
                bounds = BoundingBox(tuple(cv2.boundingRect(contour)))
                # cv2.rectangle(image, (bounds.x, bounds.y), (bounds.x + bounds.w, bounds.y + bounds.h), (0, 255, 0), 5)
                boxes.append(bounds)
            self.bounding_boxes.append(boxes)

        return

    def merge_overlapping_bounding_boxes(self):
        assert self.bounding_boxes, "No boxes in ImageProcessing.bounding_boxes"

        for i, pack in enumerate(zip(self.images, self.bounding_boxes)):
            image, boxes = pack
            merged_boxes = list()

            for box in boxes:
                overlap = False
                for m_box in merged_boxes:
                    if m_box.check_overlap(box, 18):
                        overlap = True
                        x = min(box.x, m_box.x)
                        y = min(box.y, m_box.y)
                        w = max(box.x + box.w, m_box.x + m_box.w)
                        h = max(box.y + box.h, m_box.y + m_box.h)
                        box.x, box.y, box.w, box.h = x, y, w, h
                if not overlap:
                    merged_boxes.append(box)

            self.bounding_boxes[i] = merged_boxes
            # this method could do with a lot of improvement

    # this method perfectly cropped all body text pages without issue
    # however, it is overzealous and sometimes cropped out text where no running header existed
    # such as chapter titles
    # TODO: make less zealous
    def crop_running_header(self):
        assert self.bounding_boxes, "No bounding boxes in ImageProcessing.bounding_boxes"

        for i, pack in enumerate(zip(self.images, self.bounding_boxes)):
            image, bounds = pack

            bounds.sort(key=lambda x: x.y)
            height = image.shape[0]
            width = image.shape[1]

            top_margin = height * 0.2  # TODO: make this a configurable value

            for box in bounds:
                if box.y < top_margin and box.h / box.w < 0.3:
                    y1 = max(0, box.y-3)
                    y2 = min(box.y + box.h+3, height)
                    x1 = max(0, box.x-3)
                    x2 = min(box.x + box.w+3, width)

                    aoi = image[y1:y2, x1:x2]
                    is_header: str = tesseract.image_to_string(aoi)
                    is_header = re.sub(r'[^a-zA-Z0-9]', r'', is_header)
                    if is_header and is_header.isalpha():
                        self.images[i] = image[box.y+box.h+3:]
                        self.bounding_boxes[i] = [box for box in bounds if box.y > y2]  # discard all cropped boxes

                        new_height = self.images[i].shape[0]
                        difference = height - new_height
                        new_bounds = []
                        for m_box in bounds:
                            m_box.y -= difference
                            if m_box.y >= 0:
                                new_bounds.append(m_box)

                        self.bounding_boxes[i] = new_bounds
                        break

    # TODO: crop bottom of page number method

    def crop_body_text(self):
        assert self.bounding_boxes, "No bounding boxes in ImageProcessing.bounding_boxes"

        for i, pack in enumerate(zip(self.images, self.bounding_boxes)):
            image, bounds = pack

            x = [box.x for box in bounds]
            y = [box.y for box in bounds]
            w = [box.w for box in bounds]
            h = [box.h for box in bounds]

            x1 = min(x)
            x2 = max(x) + max(w)
            y1 = min(y)
            y2 = max(y) + max(h)

            self.images[i] = image[y1:y2, x1:x2]

            # unlike crop_header_detection we don't bother modifying the bounds list
            # because this should be the end of the pre-process preparation
            # if in future this is no longer the end point, modify the bounds list
            # see crop_header_detection for how to do so

            return

    def save_images(self):
        assert self.images, "No images in ImageProcessing.images"

        for file, image in zip(self.files, self.images):
            cv2.imwrite(f"{str(file)}_canny.jpg", image)

    def get_memory_size(self):
        size = 0
        size += sys.getsizeof(self)
        for file in self.files:
            size += sys.getsizeof(file)
        for image in self.images:
            size += sys.getsizeof(image)
        for contour in self.contours:
            size += sys.getsizeof(contour)
        for bounding_box in self.bounding_boxes:
            size += sys.getsizeof(bounding_box)
        print(f"Size of {self}: {size}.")
