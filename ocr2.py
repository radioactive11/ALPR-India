import cv2
import pytesseract
import os
import re

os.chdir("cropped/")
img_list = os.listdir()

for img in img_list:
    if(os.path.splitext(img)[1] == ".jpg"):
        image = cv2.imread(img)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (300, 50), interpolation=cv2.INTER_CUBIC)    
        dn_gray = cv2.fastNlMeansDenoising(resized, templateWindowSize=7, h=25)
        gray_bin = cv2.threshold(dn_gray, 80, 255, cv2.THRESH_BINARY)[1]
        txt = pytesseract.image_to_string(gray_bin)
        if((len(txt) > 0)and (txt[0].isdigit())):
            txt = txt[1:]
        result = re.sub('[\W_]+', '', txt) # RegEx to remove all chars that are not alpha/numeric
        result = ''.join(ch for ch in result if (ch.isupper() or ch.isnumeric()))
        cv2.imshow("Detection", gray_bin)
        print(result)
        print("Press any key")
        cv2.waitKey()
