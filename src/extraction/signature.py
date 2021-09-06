import cv2 as cv
from skimage import measure
from skimage.measure import regionprops

from ..storage.storage_service import get_image_file_path, get_num_pages

sign_ext_param = {
    'MIN_AREA': 7500,
    'MAX_WIDTH': 700,
    'MAX_HEIGHT': 700,
    'REGION_AREA_INIT': 200,
    'REGION_AREA': 1200,
    'A4_MLT': 200.0,
    'A4_DIV': 85.0,
    'A4_ADD': 100.0
}


def filter_signature_by_shape_size_profile(bbox_collection):

    filtered_bbox_collection = []

    min_area = sign_ext_param['MIN_AREA']
    max_width = sign_ext_param['MAX_WIDTH']
    max_height = sign_ext_param['MAX_HEIGHT']

    min_bbox_area = 1_000_000_000
    max_bbox_area = -1

    for bbox in bbox_collection:
        x1, y1, x2, y2 = bbox
        bbox_area = (x2 - x1) * (y2 - y1)
        if bbox_area > max_bbox_area:
            max_bbox_area = bbox_area
        if bbox_area < min_bbox_area:
            min_bbox_area = bbox_area
    avg_bbox_area = (min_bbox_area + max_bbox_area) / 2.

    for bbox in bbox_collection:
        y1, x1, y2, x2 = bbox
        bbox_width = x2 - x1
        bbox_height = y2 - y1
        bbox_area = bbox_width * bbox_height
        if bbox_area > avg_bbox_area and bbox_area > min_area and bbox_width < max_width and bbox_height < max_height:
            filtered_bbox_collection.append(bbox)

    return filtered_bbox_collection


def extract_signature(doc_id):
    num_pages = get_num_pages(doc_id)

    result_list = []
    for page in range(num_pages):
        file_img = get_image_file_path(doc_id, page, num_pages)
        image_handler = cv.imread(file_img, 0)
        bbox_collection = perform_signature_extraction(image_handler)
        if bbox_collection:
            for bbox in bbox_collection:
                extracted = {
                        "bbox": {'x1': bbox[1], 'y1': bbox[0], 'x2': bbox[3], 'y2': bbox[2]},
                        "page_number": page
                    }
                result_list.append(extracted)
    if result_list:
        return {"signature": {'extraction': result_list[0]}}

    return {"signature": "NOT_FOUND"}


def get_page_format_constant(average):
    # experimental-based ratio calculation,  parameterized
    return (average / sign_ext_param['A4_DIV'] * sign_ext_param['A4_DIV']) + sign_ext_param['A4_ADD']


def perform_signature_extraction(image_source):
    # connected component analysis
    blobs = image_source > image_source.mean()
    blobs_labels = measure.label(blobs, background=1)

    the_biggest_component = 0
    total_area = 0
    counter = 0

    bbox_collection = []
    for region in regionprops(blobs_labels):
        if region.area > sign_ext_param['REGION_AREA_INIT']:
            total_area = total_area + region.area
            counter = counter + 1
        # take regions with large enough areas
        if region.area >= sign_ext_param['REGION_AREA']:
            if region.area > the_biggest_component:
                the_biggest_component = region.area
    average = total_area / counter
    page_format_const = get_page_format_constant(average)

    for region in regionprops(blobs_labels):
        if region.area > page_format_const:
            res = region.bbox
            bbox_collection.append(res)

    filtered_bbox_collection = filter_signature_by_shape_size_profile(bbox_collection)

    return filtered_bbox_collection
