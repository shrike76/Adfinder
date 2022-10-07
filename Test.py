import time
from PIL import Image
import pytesseract

from bs4 import *
import os
import cv2
import numpy as np
import csv
#from fuzzywuzzy import fuzz
#uses custom_dict.py for insensitive csv file reading


#selenium 4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

directorydump = 'D:\\Users\\shrike\\Documents\\python\\main\\dump'

#output folder path
tempPath = "D:\\Users\\shrike\\Documents\\python\\main\\text"
#initializes the dict list of found companies
totalCompanyList = {}
#iterating the images inside the folder https://www.geeksforgeeks.org/python-ocr-on-all-the-images-present-in-a-folder-simultaneously/
for imageName in os.listdir(directorydump)[1:]:
            
    inputPath = os.path.join(directorydump, imageName)

    #clean up the images https://stackoverflow.com/questions/64099248/pytesseract-improve-ocr-accuracy
    img = cv2.imread(inputPath)
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    #applying ocr using pytesseract for python
    imageText = pytesseract.image_to_string(img, lang ="eng", config='--psm 4 --oem 3')
    
    fullTempPath = os.path.join(tempPath, 'time_'+imageName+".txt")
    print(imageText)

    #saving the text for every image in a separate .txt file
    file1 = open(fullTempPath, "w")
    file1.write(imageText)
    file1.close() 

    companyFound = False

        #checks line by line through the list of companies if the a company is somewhere in the imageText https://stackabuse.com/read-a-file-line-by-line-in-python/
    with open("D:\\Users\\shrike\\Documents\\python\\main\\CompanyNames.txt", 'r') as fp:
        for line in fp:
            lowerLine = line.lower()
            currentLine = lowerLine.split(",")
            if(imageText == ''):
                print("Empty text \n")
                #setting this equal to true here so line 131 does not print. 
                companyFound = True
                break
            i = 0
            while i < len(currentLine):
                if currentLine[i] in imageText.lower():
                    print("Company found: " + line + "\n")
                    companyFound = True
                    #checks if found company is in dict list, and if not puts it there and adds +1 to the count
                    if line not in totalCompanyList:
                        totalCompanyList[currentLine[0]] = 0
                    totalCompanyList[currentLine[0]] += 1
                i += 1
    if companyFound != True:
        print("Company not found \n")

print(totalCompanyList)