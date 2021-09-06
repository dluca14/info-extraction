import re
import xml.etree.ElementTree as ET

ELEMENT_BY_CLASS = ".//*[@class='%s']"
PAGE_BY_ID = ".//*[@id='page_%d']//*[@class='%s']"
OCR_PAGE = "ocr_page"
OCR_AREA = "ocr_carea"
OCR_PAR = "ocr_par"
OCR_LINE = "ocr_line"
OCRX_WORD = "ocrx_word"

class HOCR:

    def __init__(self, hocr_content):
        self.hocr = ET.fromstring(hocr_content)


    @staticmethod
    def text(node):
        if node.text:
            s = node.text
        else:
            s = ''
        s += ' '.join([n.text for n in node.findall(".//*") if n.text is not None])
        return re.sub(r'\s+', ' ', s)

    @staticmethod
    def bbox(node):
        title = node.get("title")
        for part in title.split(';'):
            part = part.strip()
            if part.startswith('bbox'):
                box = part.split(' ')
                xtl = int(box[1])
                ytl = int(box[2])
                xbr = int(box[3])
                ybr = int(box[4])
                return (xtl, ytl), (xbr, ybr)

        print("Couldn't find bbox in title: " + title)
        return None

    @staticmethod
    def get_elements_inside_node(parent_node, which=OCRX_WORD):
        xpath = ELEMENT_BY_CLASS % which
        return [node for node in parent_node.findall(xpath, namespaces={"re": "http://exslt.org/regular-expressions"})];

    def __extract(self, which=OCR_LINE, page=None):
        if page is not None:
            xpath = PAGE_BY_ID % (page, which)
        else:
            xpath = ELEMENT_BY_CLASS % which
        return [
            (node, self.bbox(node)) for node in self.hocr.findall(xpath, namespaces={"re": "http://exslt.org/regular-expressions"})
        ]

    def __extract_raw_string(self, which=OCR_LINE, page=None):
        if page is not None:
            xpath = PAGE_BY_ID % (page, which)
        else:
            xpath = ELEMENT_BY_CLASS % which
        return [
            ET.tostring(node) for node in self.hocr.findall(xpath, namespaces={"re": "http://exslt.org/regular-expressions"})
        ]


    def pages_count(self):
        return len(self.hocr.findall(ELEMENT_BY_CLASS % OCR_PAGE))

    def pages(self, page=None):
        return self.__extract(OCR_PAGE, page=page)

    def pages_raw_string(self, page=None):
        return self.__extract_raw_string(OCR_PAGE, page=page)

    def areas(self, page=None):
        return self.__extract(OCR_AREA, page=page)

    def paragraphs(self, page=None):
        return self.__extract(OCR_PAR, page=page)

    def lines(self, page=None):
        return self.__extract(OCR_LINE, page=page)

    def words(self, page=None, regex=None):
        return self.__extract(which=OCRX_WORD, page=page)

if __name__ == "__main__":
    print('test')