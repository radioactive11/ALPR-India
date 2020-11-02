import cv2
import pytesseract
import os
import re

from pytesseract.pytesseract import image_to_boxes


# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


img = cv2.imread("cropped/2.jpg")
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
img = cv2.resize(img, (300, 50), interpolation=cv2.INTER_CUBIC)

img = cv2.fastNlMeansDenoising(img, templateWindowSize=7, h=25)
img = cv2.threshold(img, 80, 255, cv2.THRESH_BINARY)[1]

img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,11,2)
txt = pytesseract.image_to_string(img)

if((len(txt) > 0)and (txt[0].isdigit())):
    txt = txt[1:]
result = re.sub('[\W_]+', '', txt) # RegEx to remove all chars that are not alpha/numeric
result = ''.join(ch for ch in result if (ch.isupper() or ch.isnumeric()))

cv2.imshow("Detection", img)
print(result)
print("Press any key")
cv2.waitKey()