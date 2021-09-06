
import cv2 as cv
import numpy as np

MAX_CONTOUR_COUNT = 500
COL_WHITE = (255, 255, 255)
MSK_PAD = 1

params = {
    "MIN_LIN_LENGTH" : 50,
    "MAX_LINE_GAP" : 10
}


def extract_page_without_text(image_path, mask_color=COL_WHITE):
    """
    @param image_path - path to the image from which to extract text
    @param mask_color - color mask to use
    Extract from the original image an image with only lines, not text
    Note: large size text might be not removed
    """
    # Read the image and make a copy then transform it to gray colorspace,
    # threshold the image and search for contours.
    img = cv.imread(image_path)
    res = img.copy()
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    _, thresh = cv.threshold(gray,0,255,cv.THRESH_BINARY_INV+cv.THRESH_OTSU)
    _, contours, hierarchy = cv.findContours(thresh,cv.RETR_TREE,cv.CHAIN_APPROX_NONE)

    # Iterate through contours and draw a slightly bigger white rectangle
    # over the contours that are not big enough (the text) on the copy of the image.
    for i in contours:
        cnt = cv.contourArea(i)
        if cnt < MAX_CONTOUR_COUNT:
            x,y,w,h = cv.boundingRect(i)
            cv.rectangle(res,(x-MSK_PAD,y-MSK_PAD),(x+w+MSK_PAD,y+h+MSK_PAD),mask_color,-1)

    return res


def extract_lines_from_image_houghsp(image_path, params):
    """
    @param image_path - path to the image to process for line extraction
    @param params - parameters for the Hough transform based line extraction

    Extract lines from an image using Hough Transform for lines
    We are using Hough transform and not horizontal & vertical line extraction due to possible image tilt
    """

    image_without_text = extract_page_without_text(image_path)
    # Convert the resulting image from first step (no text) to gray colorspace.
    res = image_without_text.copy()
    gray = cv.cvtColor(res, cv.COLOR_BGR2GRAY)

    # Use Canny edge detection and dilate the edges for better result.
    edges = cv.Canny(gray, 50, 150, apertureSize=3)
    kernel = np.ones((4, 4), np.uint8)
    dilation = cv.dilate(edges, kernel, iterations=1)

    # Perform HoughLinesP tranform.
    minLineLength = params.get("MIN_LIN_LENGTH")
    maxLineGap = params.get("MAX_LINE_GAP")
    lines = cv.HoughLinesP(dilation, 1, np.pi / 180, 50, minLineLength, maxLineGap)
    for line in lines:
        for x1, y1, x2, y2 in line:
            cv.line(res, (x1, y1), (x2, y2), (0, 255, 0), 2)
    return res, lines


def sort_contours(contours, method="left-to-right"):
    """
    @param contours - contours to sort
    @param method - method to use in contour sorting ("left-to-right"/"right-to-left"/"bottom-to-top"/"top-to-bottom")

    Sort the contours according to the logic given by method
    Extract then the bounding boxes from the sorted contours
    Returns the sorted contours list and the bounding boxes list
    """
    # initialize the reverse flag and sort index
    reverse = False
    i = 0
    # handle if we need to sort in reverse
    if method == "right-to-left" or method == "bottom-to-top":
        reverse = True
    # handle if we are sorting against the y-coordinate rather than
    # the x-coordinate of the bounding box
    if method == "top-to-bottom" or method == "bottom-to-top":
        i = 1
    # construct the list of bounding boxes and sort them from top to
    # bottom
    bounding_boxes = [cv.boundingRect(c) for c in contours]
    (contours, bounding_boxes) = zip(*sorted(zip(contours, bounding_boxes),
                                             key=lambda b: b[1][i], reverse=reverse))

    # return the list of sorted contours and bounding boxes
    return (contours, bounding_boxes)


def find_contours_and_bounding_boxes(image, method="top-to-bottom"):
    """
    @image - image to process to find contours and corresponding bounding boxes list
    Returns sorted contours list (using the selected method) and corresponding bounding boxes list
    """
    image = cv.cvtColor(image, cv.COLOR_BGR2GRAY);
    thresh,img_bin = cv.threshold(image,128,255,cv.THRESH_BINARY |cv.THRESH_OTSU)
    # Detect contours for following box detection
    contours = cv.findContours(img_bin, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    print(len(contours), len(contours[0]), len(contours[1]))
    #contours, hierarchy = find_contours(image_without_text)
    # Sort all the contours by top to bottom.
    contours, bounding_boxes = sort_contours(contours[1], method=method)
    return contours, bounding_boxes


def create_table_structure(bounding_boxes):
    bboxes = []
    for bbox in bounding_boxes:
        x, y, w, h = bbox
        if 20 < w < 1000 and 20 < h < 500:
            bboxes.append(bbox)

    # Creating a list of heights for all detected boxes
    heights = [bboxes[i][3] for i in range(len(bboxes))]
    # Get mean of heights
    mean = np.mean(heights)
    print(mean)

    # Creating two lists to define row and column in which cell is located
    row = []
    column = []
    j = 0
    # Sorting the boxes to their respective row and column
    for i in range(len(bboxes)):
        if (i == 0):
            column.append(bboxes[i])
            previous = bboxes[i]
        else:
            if (bboxes[i][1] <= previous[1] + mean / 2):
                column.append(bboxes[i])
                previous = bboxes[i]
                if (i == len(bboxes) - 1):
                    row.append(column)
            else:
                row.append(column)
                column = []
                previous = bboxes[i]
                column.append(bboxes[i])
    print(len(column))
    print(len(row), len(row[1]))

    countcol = 0
    for i in range(len(row)):
        countcol = len(row[i])
        if countcol > countcol:
            countcol = countcol
    print(countcol)