import os
import re
from collections import defaultdict

import pytesseract

from PIL import Image
import cv2
from cv2 import cv2
import numpy as np
from collections import defaultdict
import db as db
#from db import add_item, add_receipt, check_store

#open cv accepts BGR, while pytesseract accepts RBG
from pytesseract import Output

def image2Text():
#file_path
    # pytesseract.pytesseract.tesseract_cmd= r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    config = r"--oem 3 --psm 6"

    #load image
    image= cv2.imread("realWalmart4.jpg")
    image = preProcess(image)
    recieptTxt = pytesseract.image_to_string(image, config=config)
    splitText = recieptTxt.splitlines()

    #print(recieptTxt)
    #print(splitText)

    product_catalog=defaultdict(int)
    product_catalog=image2Data(splitText,product_catalog)
    outputToSql(product_catalog)
    

#This function converts all the images in the directory 
#and inputs it to the Database
def directory2Text():
    inventory_list = [{}]
    # pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    config = r"--oem 3 --psm 6"
    
    path=os.getcwd()
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
            #print(recieptTxt)
            #print(splitText)

            product_catalog = image2Data(splitText,product_catalog)
            print(product_catalog)
            outputToSql(product_catalog)
            
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



def image2Data(splitText, product_catalog):
    #Parsing Patterns
    product_pattern=re.compile(r'([A-Z\s_.]+)[\d\s]+..?\s?\${0,1}(\d+\.\d{2})')
    total_pattern=re.compile(r'(SUBTOTAL|TOTAL)([/s0-9])*', re.IGNORECASE)
    store_pattern=re.compile(r'(WALMAR|TARGET|COSTCO|SAM\'S)', re.IGNORECASE)
    address_pattern=re.compile(r'.+(\d{4}\s\w+)$', re.IGNORECASE)


    for line in splitText:
        #Searches for Product Name and Price
        if re.search(product_pattern, line):
            product_line=product_pattern.search(line)
            product_catalog[product_line.group(1)]=product_line.group(2)
        #Searches for Total and Subtotal
        elif re.search(total_pattern, line):
            #print("subtotal and total",line)
            total_line = total_pattern.search(line)
            product_catalog[total_line.group(1)]=0
            product_catalog[total_line.group(1)]=total_line.group(2)
        #Searches for Store Name
        elif re.search(store_pattern, line):
            #print("store name", line)
            store_line = store_pattern.search(line)
            product_catalog["store_name"] = store_line.group(1)
        #Searches for Store Address
        elif re.search(address_pattern, line):
            #print("This should be an address:", line)
            address_line = address_pattern.search(line)
            product_catalog["store_location"] = address_line.group(1)
    return product_catalog

def outputToSql(product_catalog):
    store_id = db.check_store(product_catalog["store_name"].lstrip(), product_catalog["location"], "")
    purchase_id= db.add_receipt(0, store_id, product_catalog["SUBTOTAL"], product_catalog["TOTAL"])
    
    for name, price in product_catalog.items():
        if name != "SUBTOTAL" and  name!= "location" and  name!="TOTAL" and name != "store_name":
            db.add_item(purchase_id, name.lstrip(), name.lstrip(), price)


def printImage(image):
    d = pytesseract.image_to_data(image, output_type=Output.DICT)
    keys = list(d.keys())

    #get boxes
    n_boxes = len(d['text'])
    for i in range(n_boxes):
        if int(d['conf'][i]) > 60:
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow('img', image)
    cv2.waitKey(0)


if __name__ == '__main__':
    image2Text()
    #directory2Text()

