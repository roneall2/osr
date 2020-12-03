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

def image2Text(image_path, userID):
    #file_path
    # pytesseract.pytesseract.tesseract_cmd= r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    config = r"--oem 3 --psm 6"
    print(image_path)
    #load image
    image= cv2.imread(image_path)
    #image= cv2.imread("walmartScannedbetter.png")

    image = preProcess(image)
    recieptTxt = pytesseract.image_to_string(image, config=config)
    splitText = recieptTxt.splitlines()

    #print(recieptTxt)
    #print(splitText)

    product_catalog=defaultdict(int)
    product_catalog=image2Data(splitText,product_catalog)
    #print(product_catalog)
    outputToSql(product_catalog, userID)

    

#This function converts all the images in the directory 
#and inputs it to the Database
def directory2Text():
    inventory_list = [{}]
    # pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    config = r"--oem 3 --psm 6"
    
    path="photos"
    i=0
    # iterate through the names of contents of the folder
    for image_path in os.listdir(path):
        if image_path.endswith(".jpg") or image_path.endswith(".png"):
            product_catalog=defaultdict(int)
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
            #print(product_catalog)
            i+=1
            outputToSqldir(product_catalog, i%9)
            #printImage(image)
    print("number of records added", len(inventory_list))











#These are helper functions

#Function to preproccess the image
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


#Function that parses through the text and 
#returns a dictionary with all the purchase items
def image2Data(splitText, product_catalog):
    #Parsing Patterns
    product_pattern = re.compile(r'([A-Z\s_.]+)[\d]+.?\s?\${0,1}(\d+\.\d{2})')
    total_pattern = re.compile(r'(SUBTOTAL|TOTAL)\${0,1}([\s0-9.]+)$', re.IGNORECASE)
    store_pattern = re.compile(r'(WALMART|TARGET|COSTCO|mart|rget|BERGDORF GODDMAN)', re.IGNORECASE)
    address_pattern=re.compile(r'^.{0,1}(\d{2,4}\s[A-Z-a-z\s]{2,})$', re.IGNORECASE)


    for line in splitText:
        #Searches for Total and Subtotal
        if re.search(total_pattern, line):
            #print("subtotal and total",line)
            total_line = total_pattern.search(line)
            product_catalog[total_line.group(1)]=total_line.group(2)
        #Searches for Store Name
        elif re.search(store_pattern, line):
            #print("store name", line)
            store_line = store_pattern.search(line)
            if "mart" in store_line.group(1) or "wal" in store_line.group(1):
                product_catalog["store_name"] = "WALMART"
                continue
            if "co" in store_line.group(1) and "so" in store_line.group(1):
                product_catalog["store_name"] = "COSTCO"
                continue
            product_catalog["store_name"] = store_line.group(1)
        #Searches for Store Address
        elif re.search(address_pattern, line):
            #print("This should be an address:", line)
            address_line = address_pattern.search(line)
            product_catalog["store_location"] = line
        #Searches for Product Name and Price
        elif re.search(product_pattern, line):
            product_line=product_pattern.search(line)
            product_catalog[product_line.group(1)]=product_line.group(2)
    return product_catalog

#Inputs purchased data into database for a SINGLE photo
def outputToSql(product_catalog, userID):
    store_id = db.check_store(str(product_catalog["store_name"]).lstrip(), product_catalog["store_location"], "")
    purchase_id= db.add_receipt(userID , store_id, product_catalog["SUBTOTAL"], product_catalog["TOTAL"])
    checks=["SUBTOTAL",  "TOTAL","store_name" ,"store_location", "TAX" , "CASH" , "CHANGE" , "VISA"]
    for name, price in product_catalog.items():
        name.lstrip()
        #if name not in checks:
        if ("OTAL" not in name and name != "store_name" and name!= "store_location" and
         "TAX" not in name and "CASH" not in name and "CHANGE" not in name and "VISA" not in name and "CARD" not in name):
            #print(purchase_id, name.lstrip(), name.lstrip(), price)
            db.add_item(purchase_id, str(name).lstrip(), str(name).lstrip(), price)


#Inputs purchased data into database for all photos in directory
def outputToSqldir(product_catalog, userID):

    db.initialize_cursor()
    store_id = db.check_store(str(product_catalog["store_name"]).lstrip(), product_catalog["store_location"], "")
    purchase_id= db.add_receipt(userID, store_id, product_catalog["SUBTOTAL"], product_catalog["TOTAL"])
    checks=["SUBTOTAL",  "TOTAL","store_name" ,"store_location", "TAX" , "CASH" , "CHANGE" , "VISA"]
    for name, price in product_catalog.items():
        name.lstrip()
        #if name not in checks:
        if ("OTAL" not in name and name != "store_name" and name!= "store_location" and "REFUND" not in name and
         "TAX" not in name and "CASH" not in name and "CHANGE" not in name and "VISA" not in name and "CARD" not in name):
            db.add_item(purchase_id, str(name).lstrip(), str(name).lstrip(), price)

#prints the image with bounding boxes
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

def demo_setup():
    image2Text("photos/costco2.jpg", 0)
    image2Text("photos/costco3.jpg", 1)
    image2Text("photos/costco4.jpg", 2)
    image2Text("photos/realWalmart1.jpg", 3)
    image2Text("photos/realWalmart2.jpg", 4)
    image2Text("photos/realWalmart3.jpg", 5)
    image2Text("photos/realWalmart4.jpg", 6)
    image2Text("photos/target1.jpg", 7)
    image2Text("photos/target3.jpg", 8)
    image2Text("photos/target6.jpg", 9)
    image2Text("photos/target7.jpg", 8)
    image2Text("photos/target8.jpg", 4)
    image2Text("photos/target9.jpg", 2)
    image2Text("photos/target10.jpg", 1)
    image2Text("photos/walmart_test.png", 6)


if __name__ == '__main__':
    #image2Text()
    # 
    directory2Text()

