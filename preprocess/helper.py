import os
from enum import IntFlag
from pathlib import Path
from statistics import median
from sys import exit

import cv2
import numpy
from PIL import Image
from numpy import ndarray

from utils.exception import EmptyDirectoryError
from utils.status import warn, info
from utils.system import DirectoryContents


class ImgManipFlags(IntFlag):
    NoFlags = 0
    CropRunningHeader = 1 << 1
    CropPageNumber = 1 << 2
    ResizeImage = 1 << 3


class BoundingBox:
    def __init__(self, bounds: tuple[int, ...]):
        try:
            if len(bounds) != 4:
                raise IndexError("bounds must have 4 indices: x, y, w, h.")
        except IndexError as e:
            warn(e)
            exit(1)

        self.x = int(bounds[0])
        self.y = int(bounds[1])
        self.w = int(bounds[2])
        self.h = int(bounds[3])
        self.bounds = bounds

    def __iter__(self):
        return iter(self.bounds)

    def __len__(self):
        return len(self.bounds)

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.x == other.x and self.y == other.y and self.w == other.w and self.h == other.h)

    def __hash__(self):
        return hash((self.x, self.y, self.w, self.h))

    def __repr__(self):
        return f"x: {self.x}, y: {self.y}, w: {self.w}, h: {self.h}"

    def check_overlap(self, comp, dilate: int = 0):
        return (self.x - dilate <= comp.x <= self.x + self.w + dilate
                and self.y - dilate <= comp.y <= self.y + self.h + dilate)

    def size(self) -> int:
        return self.w * self.h


def binarise_image(path: Path) -> None:
    image: ndarray
    binary: ndarray

    try:
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    except cv2.error as e:
        warn(e)
        info(f"Error path: {path}.")
        exit(1)

    image = cv2.bilateralFilter(image, 3, 15, 15)
    _, binary = cv2.threshold(image, 240, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = numpy.ones((15, 15), numpy.uint16)
    binary = cv2.dilate(binary, kernel, iterations=2)

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    a = [cv2.contourArea(contour) for contour in contours]
    a.sort()

    # TODO:
    """
    get horizontal rectangles --- these are likely text
    then we sort them by size and descard any significantly small ones
    these are probably abberations
    """

    # return BoundingBox(tuple(cv2.boundingRect(text_region)))

    # _, file = path.parts
    # path = Path('bin', file)
    path = "test2.jpg"

    try:
        if not cv2.imwrite(str(path), binary):
            raise NotADirectoryError(f"Directory not found at {str(path)}.")
    except NotADirectoryError as e:
        warn(e)
        exit(1)

    return


def batch_binarise_images(directory: str, file_format: str = 'JPEG') -> None:
    try:
        if not os.path.isdir(directory):
            raise NotADirectoryError(f"The path '{directory}' does not point to a valid directory.")
        elif not os.listdir(directory):
            raise EmptyDirectoryError(directory)
    except (NotADirectoryError, EmptyDirectoryError) as e:
        warn(e)
        exit(1)

    dir_contents = DirectoryContents([Path(directory, item) for item in os.listdir(directory)])
    dir_contents.sort()
    dir_contents.clear_except('.jpg')

    page_count = len(dir_contents) - 1
    contours = list()
    image_data = list()

    print("Binarising images.")
    """
    for i, path in enumerate(dir_contents):
        image, binary = preprocess_image(f"{directory}/{path}")
        body_text = find_body_text(binary)
        cropped_image = crop_image(image, body_text)
        path = path.replace('a', 'b')
        save_cropped_image(cropped_image, f"{directory}/{path}")

        print(f"\rImages processed: {i} out of {page_count}.", end='', flush=True)
    """

    for image in dir_contents:
        binarise_image(image)

    print("\nBinarising complete.", end='\n\n')

    return


def preprocess_image(path: Path) -> tuple[ndarray, ndarray]:

    """
    Preprocess an image for manipulation.

    Read the image; convert to greyscale; convert to binary; invert binary data.

    returns: image, binary
    """
    image: ndarray
    binary: ndarray

    image = cv2.imread(str(path), cv2.IMREAD_COLOR)

    try:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    except cv2.error as e:
        warn(e)
        info(f"Error path: {path}.")
        exit(1)

    image = cv2.bilateralFilter(image, 9, 75, 75)
    _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = numpy.ones((7, 7), numpy.uint16)
    binary = cv2.dilate(binary, kernel, iterations=3)

    return image, binary


def preprocess_image_batch(paths: DirectoryContents) -> list[tuple]:

    """
    Preprocess images for manipulation in a batch.

    Calls the individual preprocess_image function and packs all the results into the return.

    Returns
    -------
    Return:
        packs[images, binaries].
    """

    pack: tuple[ndarray, ndarray]

    for path in paths:
        yield preprocess_image(path)


def find_body_text(binary: ndarray) -> BoundingBox:

    """
    Use contours to find body text of page.

    returns: body_text
    """

    contours: tuple
    text_region: ndarray

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    text_region = max(contours, key=cv2.contourArea)
    return BoundingBox(tuple(cv2.boundingRect(text_region)))


def find_body_text_batch(binaries: list[ndarray]) -> BoundingBox:

    """
    Use contours to find body text of page.
    Batched to estimate area from a range of image data.

    returns: body_text
    """

    contours: list[cv2.boundingRect]

    contours = list(find_body_text(binary) for binary in binaries)
    xs, ys, ws, hs = zip(*contours)

    x = int(min(xs))
    y = int(median(ys))
    w = int(max(ws))
    h = int(median(hs))
    """
    x = int(min(xs))
    y = int(mode(ys))
    w = int(max(ws))
    h = int(mode(hs))
    """

    composite = BoundingBox((x, y, w, h))

    return composite


def crop_image(image: ndarray, binary: ndarray, crop_area: BoundingBox) -> ndarray:
    """
    Crop image data using bounding box as constraint.
    Batched to crop from a range of images.

    returns: cropped_image
    """

    # TODO:
    """
    basically just get the median contour box from all images
    then get contours again from XYZ page
    then begin the cropping at the x,y of the largest contour
    and apply the height from the median contour box
    """

    text_area = find_body_text(binary)
    return image[text_area.y: text_area.y + crop_area.h, crop_area.x: crop_area.x + crop_area.w]


def crop_image_batch(images: list[ndarray], binaries: list[ndarray], crop_area: BoundingBox) -> ndarray:
    """
    Crop image data using bounding box as constraint.

    returns: cropped_image
    """

    for image, binary in zip(images, binaries):
        yield crop_image(image, binary, crop_area)


def save_cropped_image(cropped_image: ndarray, path: str, file_format: str) -> None:
    """
    Save cropped image to specified filepath.
    Saves as .jpg by default.

    Parameters
    ----------
    cropped_image : ndarray
        The cropped image to save.
    path : str
        The save path. Recommend not to include extension.
    file_format : str
        The format to save. Defaults to 'JPEG'.

    Returns
    -------
    Return:
        None.
    """

    if file_format == 'JPEG' and os.path.splitext(path)[1] != '.jpg':
        path = f"{path}{'.jpg'}"
    elif file_format == 'PNG' and os.path.splitext(path)[1] != '.png':
        path = f"{path}{'.png'}"

    image = Image.fromarray(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))
    image.save(path, file_format)

    return


def batch_crop_images(directory: str, file_format: str = 'JPEG') -> None:
    try:
        if not os.path.isdir(directory):
            raise NotADirectoryError(f"The path '{directory}' does not point to a valid directory.")
        elif not os.listdir(directory):
            raise EmptyDirectoryError(directory)
    except (NotADirectoryError, EmptyDirectoryError) as e:
        warn(e)
        exit(1)

    dir_contents = DirectoryContents([Path(directory, item) for item in os.listdir(directory)])
    dir_contents.sort()
    dir_contents.clear_except('.jpg')

    page_count = len(dir_contents) - 1
    contours = list()
    image_data = list()

    print("Processing images.")
    """
    for i, path in enumerate(dir_contents):
        image, binary = preprocess_image(f"{directory}/{path}")
        body_text = find_body_text(binary)
        cropped_image = crop_image(image, body_text)
        path = path.replace('a', 'b')
        save_cropped_image(cropped_image, f"{directory}/{path}")

        print(f"\rImages processed: {i} out of {page_count}.", end='', flush=True)
    """

    for image, binary in preprocess_image_batch(dir_contents):
        image_data.append(image)
        contours.append(binary)

    crop_area = find_body_text_batch(contours)

    assert len(image_data) == len(contours), f"image_data len({len(image_data)} != contours len({len(contours)}))"

    for i, cropped_image in zip(range(len(image_data)), crop_image_batch(image_data, contours, crop_area)):
        path = f"{i}_b"
        save_cropped_image(cropped_image, f"{directory}/{path}", file_format)

    print("\nProcessing complete.", end='\n\n')

    return
