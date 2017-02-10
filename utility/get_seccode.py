from selenium import webdriver
import pytesseract
from PIL import Image, ImageEnhance


def get_verify_num(name):
    """
    get the number of img.
    """
    threshold = 100
    matrix = list()
    for px in range(256):
        if px < threshold:
            matrix.append(0)
        else:
            matrix.append(1)
    rep = {
        ']': 'J',
        '13': 'B'
    }
    im = Image.open(name)
    ima = im.convert('L')
    img = ImageEnhance.Sharpness(ima).enhance(1)
    img.save('g.jpg')
    out = img.point(matrix, '1')
    out.save('b.jpg')
    text = pytesseract.image_to_string(out)
    text = text.strip()
    text = text.upper()
    for r in rep:
        text = text.replace(r, rep[r])
        text = text.replace(' ', '')
    return text


if __name__ == "__main__":
    print get_verify_num('D:/code.jpg')
