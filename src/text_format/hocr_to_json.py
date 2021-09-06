from .hocr import HOCR
import re


def extract_hocr_json(hocr_content):
    hocr = HOCR(hocr_content);

    for i, page_div in enumerate(hocr.pages()):
        page_bbox = page_div[1]
        words = []

        page_lines = hocr.get_elements_inside_node(page_div[0], 'ocr_line')
        if len(page_lines) > 0:
            for line in page_lines:
                # produce here the json
                for word in line.getchildren():
                    word_bbox = hocr.bbox(word)
                    word_obj = {}
                    word_obj['id'] = re.sub('_.*_', '_', word.get('id'))
                    word_obj['line'] = re.sub('_.*_', '_', line.get('id'))
                    word_obj['x1'] = int(word_bbox[0][0])
                    word_obj['y1'] = int(word_bbox[0][1])
                    word_obj['x2'] = int(word_bbox[1][0])
                    word_obj['y2'] = int(word_bbox[1][1])
                    word_obj['t'] = ''.join([w for w in word.itertext()])

                    words.append(word_obj)

        result = {}
        result['width'] = int(page_bbox[1][0])
        result['height'] = int(page_bbox[1][1])
        result['words'] = words

        return result
