import os
import re
from collections import defaultdict

import pytesseract
from PIL import Image
import cv2
from cv2 import cv2
import numpy as np

#open cv accepts BGR, while pytesseract accepts RBG
from pytesseract import Output

def image2Text():
#file_path
    pytesseract.pytesseract.tesseract_cmd= r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    config = r"--oem 3 --psm 6"
    print('hello world')

    #load iamge
    image= cv2.imread("walmart1.jpg")
    image = preProcess(image)
    recieptTxt = pytesseract.image_to_string(image, config=config)
    splitText = recieptTxt.splitlines()
    print(recieptTxt)
    print(splitText)

    product_catalog={}
    product_catalog=image2Data(splitText,product_catalog)
    print(product_catalog)
    printImage(image)

def directory2Text():
    inventory_list = [{}]
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    config = r"--oem 3 --psm 6"
    print('hello world')
    path=r"C:\Users\bassel\PycharmProjects\OCR"
    # iterate through the names of contents of the folder
    for image_path in os.listdir(path):
        if image_path.endswith(".jpg") or image_path.endswith(".png"):
            product_catalog={}
            inventory_list.append(product_catalog)
            # create the full input path and read the file
            input_path = os.path.join(path, image_path)
            print(input_path)
            # load image
            image = cv2.imread(input_path)
            image = preProcess(image)
            recieptTxt = pytesseract.image_to_string(image, config=config)
            splitText = recieptTxt.splitlines()
            print(recieptTxt)
            print(splitText)

            product_catalog = image2Data(splitText,product_catalog)
            print(product_catalog)
            #printImage(image)
        else:
            continue
    print("number of records", len(inventory_list))



def preProcess(image):
    image = cv2.resize(image, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)

    #Preproccess
    image= cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # performs Erosion then Dilation on image - Openning
    # kernel = np.ones((1,1),np.uint8)
    # image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
    #kernel = np.ones((1, 1), np.uint8)
    #image = cv2.dilate(image, kernel, iterations=1)
    #image = cv2.erode(image, kernel, iterations=1)

    # #Deblur
    #image = cv2.medianBlur(image,1)


    #image=cv2.threshold(cv2.bilateralFilter(image, 5, 75, 75), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    #image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


    return image



#
# def process_image_for_ocr(file_path):
#     # TODO : Implement using opencv
#     temp_filename = set_image_dpi(file_path)
#     im_new = remove_noise_and_smooth(temp_filename)
#     return im_new
#
# def set_image_dpi(file_path):
#     im = Image.open(file_path)
#     length_x, width_y = im.size
#     factor = max(1, int(IMAGE_SIZE / length_x))
#     size = factor * length_x, factor * width_y
#     # size = (1800, 1800)
#     im_resized = im.resize(size, Image.ANTIALIAS)
#     temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
#     temp_filename = temp_file.name
#     im_resized.save(temp_filename, dpi=(300, 300))
#     return temp_filename
#
# def image_smoothening(img):
#     ret1, th1 = cv2.threshold(img, BINARY_THRESHOLD, 255, cv2.THRESH_BINARY)
#     ret2, th2 = cv2.threshold(th1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#     blur = cv2.GaussianBlur(th2, (1, 1), 0)
#     ret3, th3 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#     return th3
#
# def remove_noise_and_smooth(file_name):
#     img = cv2.imread(file_name, 0)
#     filtered = cv2.adaptiveThreshold(img.astype(np.uint8), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 41,
#                                      3)
#     kernel = np.ones((1, 1), np.uint8)
#     opening = cv2.morphologyEx(filtered, cv2.MORPH_OPEN, kernel)
#     closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
#     img = image_smoothening(img)
#     or_image = cv2.bitwise_or(img, closing)
#     return or_image


def image2Data(splitText, product_catalog):
    #Item: Brand, Name, Price
    ##Read and Output text
    items=[]
    date_pattern = r'\d\d\d.[)].\d\d\d...\d\d\d\d'
    products=[]
    prices=[]
    #date = '^\d{1,2}\/\d{1,2}\/\d{4}$'
    #product_pattern=re.compile(r'[0-9\s]*([A-Z\d{0,3}.\s]+)(\s|\d{3,}\s|\w{0,2}\s)\$+(\d+\.\d{2})(\s|\b)+')

    product_pattern=re.compile(r'([A-Z\s_.]+)[\d\s]+..?\s?\${0,1}(\d+\.\d{2})')
    total_pattern=re.compile(r'(SUBTOTAL|TOTAL)([/s0-9])*')
    store_pattern=re.compile(r'(WALMAR|TARGET|COSTCO|SAM\'S)')

    #productPattern=r'\s(\d+)\s(\d+\.\d{2})'
    productPattern=re.compile(r'\d*\.\d\d')

    #([A-Z0-9.\s])
    for line in splitText:
      if re.search(date_pattern,line):
          items.append(line)
          product_line = productPattern.search(line)
          print("first loop",product_line)
      # elif re.match(price_pattern, line):
      #    date= line
      elif re.search(product_pattern, line):
          product_line=product_pattern.search(line)
          print("second loop",product_line.group(1))
          products.append(product_line.group(1))
          prices.append(product_line.group(2))
          product_catalog[product_line.group(1)]=product_line.group(2)
      elif re.search(total_pattern, line):
          print("subtotal and total",line)
          total_line = total_pattern.search(line)
          product_catalog[total_line.group(1)]=total_line.group(2)
      elif re.search(store_pattern, line):
          print("store name", line)
          store_line = store_pattern.search(line)
          product_catalog["store_name"] = store_line.group(1)

    print("date:", items)
    print("product names:", products)
    print("prices:", prices)
    #print(product_catalog)
    return product_catalog
    #print(items)


def printImage(image):
    d = pytesseract.image_to_data(image, output_type=Output.DICT)
    #print(d.keys())
    # #get specific box
    keys = list(d.keys())

    date_pattern = '^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[012])/(19|20)\d\d$'

    n_boxes = len(d['text'])
    for i in range(n_boxes):
        if int(d['conf'][i]) > 60:
            if re.match(date_pattern, d['text'][i]):
                (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                img = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.imshow('img', image)
    cv2.waitKey(0)

    #get boxes
    n_boxes = len(d['text'])
    for i in range(n_boxes):
        if int(d['conf'][i]) > 60:
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow('img', image)
    cv2.waitKey(0)




if __name__ == '__main__':
    #image2Text()
    directory2Text()





