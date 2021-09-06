import cv2 as cv
import os
import json
import matplotlib.pyplot as plt

from ..extraction.utils import bbox_helper, bbox_merge
from ..storage.storage_service import get_image_file_path, get_num_pages, get_extraction_data


def plot_image(image):
    fig, ax = plt.subplots(figsize=(30, 18))
    ax.imshow(image)
    plt.tight_layout()
    plt.show()


def plot_image_with_size(image, size=4):
    """
    @param image = image to plot
    @param size - figure size multiplicator
    Display an image preserving aspect ratio
    """
    image_width = image.shape[0]
    image_height = image.shape[1]
    fig_size_h = 4 * size
    # keep aspect ratio
    fig_size_w = fig_size_h * image_width / image_height
    fig, ax = plt.subplots(figsize=(fig_size_w, fig_size_h))
    ax.imshow(image)
    ax.set_axis_on()
    plt.tight_layout()
    plt.show()


def plot_extraction(doc_id):
    extraction_data = get_extraction_data(doc_id)
    num_pages = get_num_pages(doc_id)
    for page in range(num_pages):
        file_img = get_image_file_path(doc_id, page, num_pages)
        image_handler = cv.imread(file_img)
        image_handler = plot_add_extraction(image_handler, extraction_data, page)
        plot_image(image_handler)


def get_configuration():
    path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
    with open(f'{path}/notebooks/configuration.json', encoding="utf8") as file:
        static_configuration = json.load(file)
    return static_configuration


def convert_color(hex_color):
    h = hex_color.lstrip("#")
    return tuple(round(int(h[i:i + 2], 16), 2) for i in (0, 2, 4))


def get_details(attribute, static_configuration):
    for configuration in static_configuration:
        if configuration['attribute'] == attribute:
            return configuration['display_name'], convert_color(configuration['color'])

    return attribute, (255, 0, 0)


def plot_add_extraction(image_handler, extractions, page):

    static_configuration = get_configuration()

    font = cv.FONT_HERSHEY_SIMPLEX
    for crt_item in extractions['extraction'].items():
        feature = crt_item[0]
        display_name, color = get_details(feature, static_configuration)
        if isinstance(crt_item[1], list):
            for list_item in crt_item[1]:
                item = list_item['extraction']
                page_number = item['page_number']
                if int(page) == int(page_number):
                    if feature == 'signature':
                        (x1, y1), (x2, y2) = bbox_helper(item['bbox'])
                    else:
                        if item['label']:
                            display_name, color = get_details(item['label'], static_configuration)
                        words = item['value_words']
                        bbox_fusion = []
                        for word in words:
                            bbox_fusion.append(bbox_helper(word))
                        bbox = bbox_merge(bbox_fusion)
                        x1, y1, x2, y2 = bbox
                    cv.rectangle(image_handler, (x1 - 2, y1 - 2), (x2 + 2, y2 + 2), color, 3)
                    cv.putText(image_handler, display_name, (x1, y1 - 3), font, 1, color, 2, cv.LINE_AA)
                    if feature == "commercial_invoice":
                        cv.putText(image_handler, item["value"], (x1 + 25, y1 + 75), font, 3, color, 3, cv.LINE_AA)

        else:
            item = crt_item[1]['extraction']
            page_number = item['page_number']
            if int(page) == int(page_number):
                if feature == 'signature':
                    (x1, y1), (x2, y2) = bbox_helper(item['bbox'])
                else:
                    words = item['value_words']
                    bbox_fusion = []
                    for word in words:
                        bbox_fusion.append(bbox_helper(word))
                    bbox = bbox_merge(bbox_fusion)
                    x1, y1, x2, y2 = bbox
                cv.rectangle(image_handler, (x1 - 2, y1 - 2), (x2 + 2, y2 + 2), color, 4)
                cv.putText(image_handler,display_name, (x1, y1 - 3), font, 1, color, 3, cv.LINE_AA)
                if feature == "commercial_invoice":
                    cv.putText(image_handler, item["value"], (x1 + 25, y1 + 75), font, 3, color, 3, cv.LINE_AA)

    return image_handler


def display_image_table_lines(image_path, lines, color=(255,0,0)):
    """
    @param image_path - path to the image to display
    @param lines - list of lines to draw over the image
    @param color - color for lines disply
    Display an image with lines superposed on it
    """
    img = cv.imread(image_path)
    res = img.copy()
    for line in lines:
        for x1, y1, x2, y2 in line:
            cv.line(res, (x1, y1), (x2, y2), color, 2)
    plot_image(res)


def plot_bounding_boxes(image_path, bounding_boxes, show_table=True):
    """
    @param image_path - path to the image to plot
    @param bounding_boxes - list of bounding boxes to represent
    @param show_table - flag to show (with a different color) the largest bounding boxes - which are the actual tables

    Draw bounding boxes (shrinked so that can be easily seen) for table cells discovered and as well the bounding box of
    the table(s)
    """
    origin_image = cv.imread(image_path)

    max_img_area = origin_image.shape[0] * origin_image.shape[1] / 1.1

    font = cv.FONT_HERSHEY_SIMPLEX
    count = 1
    for bbox in bounding_boxes:

        x, y, w, h = bbox
        # show table cells - cells are shrinked so that we can see easily the borders of each cell
        if 50 < w < 1000 and 20 < h < 500:
            count = count + 1
            cv.rectangle(origin_image, (x + 1, y + 1), (x + w - 1, y + h - 1), (0, 0, 255), 2)
            # cv.putText(origin_image, str(count), (x+int(w/2), y+int(h/2)), font, 1.5, (0, 0, 255), 2, cv.LINE_AA)
        # show tables - draw with a different color so that we can differentiate from the table cells
        if show_table and w > 1000 and h > 200 and w * h < max_img_area:
            cv.rectangle(origin_image, (x, y), (x + w, y + h), (255, 0, 0), 3)

    plot_image(origin_image)
