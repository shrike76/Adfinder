from distutils.file_util import copy_file
from logging.handlers import SYSLOG_UDP_PORT
import time
from PIL import Image
import pytesseract
import os
import cv2
import shutil
import winsound
#for pie chart
import matplotlib.pyplot as plt
import numpy
#for deleting files
import glob

#selenium 4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

#d is how many queries will be performed, initializes here at 0. 
d = 0
#initializes the dict list of found companies
totalCompanyList = {}
#FULLTEMPPATH GETS OVERWRITTEN IF C DOES NOT EXIST
c = 0
#set d < "how many times you want the program to run"
while d < 1:
    #moves the window to my second monitor (so i can game while this is running teehee)
    chrome_options = Options()
    chrome_options.add_argument("--window-position=3000,0")
    #browser exposes an executable file
    #Through Selenium test we will invoke the executable file which will then
    #invoke actual browser
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), chrome_options=chrome_options)
    #to maximize the browser window
    driver.set_window_size(2560, 1440)
    driver.maximize_window()

    #get method to launch the URL
    driver.get("https://speedtest.net/")

        #to refresh the browser
        #driver.refresh()
    #needed for ads to load
    time.sleep(4)
    #identifying the element to capture the screenshot and puts them all in a list
    try: #[contains(@href, 'ruamupr')] //*[contains(@id, 'aw0')]
        adList = driver.find_elements(By.XPATH, "//*[contains(@id, 'ads')]")   
    except:
        print("Failed to find ad")

    #for naming the files
    f = 0
    #crops all elements found above into seperate screenshots https://www.tutorialspoint.com/how-to-get-the-screenshot-of-a-particular-section-of-the-page-like-the-logo-of-a-website-in-selenium-with-python
    #step 2 is to avoid doubling of ads as each ad has 2 id = 'ads'. 
    #adList[::2]
    for i in adList[::2]:

        #to get the element location 
        location = i.location
        #to get the dimension the element
        size = i.size
        #to get the screenshot of complete page
        driver.save_screenshot("dump\cap.png")
        #to get the x axis
        x = location['x']
        #to get the y axis
        y = location['y']
        #to get the length the element
        height = location['y']+size['height']
        #to get the width the element
        width = location['x']+size['width']
        #to open the captured image
        imgOpen = Image.open("dump\cap.png")
        #check for if element is in view
        if i.is_displayed():
            #to crop the captured image to size of that element
            imgOpen = imgOpen.crop((int(x), int(y), int(width), int(height)))
            #to save the cropped image
            imgOpen.save("dump\capcropped" + str(f) + ".png")
            #iterates the naming of the files
            f+=1
        else:
            print("Can't find element")
        
    #to close the browser
    driver.close()

    #main folder path
    directorydump = 'D:\\Users\\shrike\\Documents\\python\\main\\dump'

    #output folder path
    tempPath = "D:\\Users\\shrike\\Documents\\python\\main\\text"

    adProof = "D:\\Users\\shrike\\Documents\\python\\main\\ad proof"

    #iterating the images inside the folder https://www.geeksforgeeks.org/python-ocr-on-all-the-images-present-in-a-folder-simultaneously/
    for imageName in os.listdir(directorydump)[1:]:
                
        inputPath = os.path.join(directorydump, imageName)

        #clean up the images. experimented a lot with these settings. couldn't find better ones. https://stackoverflow.com/questions/64099248/pytesseract-improve-ocr-accuracy
        img = cv2.imread(inputPath)
        img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        #applying ocr using pytesseract for python. psm 4 seems to be the best, but horizontal banner ads are still pretty hard to read. https://stackoverflow.com/questions/44619077/pytesseract-ocr-multiple-config-options
        imageText = pytesseract.image_to_string(img, lang ="eng", config='--psm 4 --oem 3')

        print(imageText)

        #variable initlizaion for printing a company was found or not later
        companyFound = False

        #checks line by line through the list of companies if the a company is somewhere in the imageText https://stackabuse.com/read-a-file-line-by-line-in-python/
        with open("D:\\Users\\shrike\\Documents\\python\\main\\CompanyNames.txt", 'r') as fp:
            for line in fp:
                #flag variable used for breaking out of nested loop. slighter faster program.
                flag = False
                if flag == True:
                    break
                #converts line to lower
                lowerLine = line.lower()
                #converts lowered line to array by splitting with comma. each line in companynames.txt is an array with each object seperated by a comma. https://stackoverflow.com/questions/21744804/how-to-read-comma-separated-values-from-a-text-file-then-output-result-to-a-tex
                currentLine = lowerLine.split(",")
                #checks if imageText is empty and breaks if so
                if(imageText == ''):
                    print("Empty text \n")
                    #setting this equal to true here so a later line does not print. 
                    companyFound = True
                    break
                i = 0
                #while loop that runs through the length of the currentLine array
                while i < len(currentLine):
                    #checks if the current object in the array is somewhere in the imageText. 
                    #this is done so companies can be identified by more than one name, and can be seperated in the CompanyNames.txt by a comma. This makes repeated ads easier to recognize. 
                    if currentLine[i] in imageText.lower():
                        #print command that identifies the company
                        print("Company found: " + line + "\n")
                        #cancels out later if command
                        companyFound = True
                        #checks if found company is in dict list, and if not puts it there and adds +1 to the count to the relevent company. currentline[0] is the first entry in an array that splits each entry in that line with a comma. Designed so only the first entry in the list is added to the dict, despite multiple possibly being detected. 
                        if currentLine[0] not in totalCompanyList:
                            totalCompanyList[currentLine[0]] = 0
                            #copies the full web screenshot each time it finds a new ad, for proof in case companies ask and data validation. 
                            shutil.copy('D:\\Users\\shrike\\Documents\\python\\main\\dump\\cap.png', adProof)
                            #s exists to remove the \n that comes out of currentLine[0]. I spent like an hour trying to get it to just print the found company name and it always had a new line or \n so I just told it to remove it. 
                            s = currentLine[0].replace('\n', '')
                            copiedAdProof = adProof + '\\' + s + '.png'
                            #renames the file path so it can be copied correctly and replaces it if it exists
                            os.replace(adProof + '\\cap.png', copiedAdProof)
                        totalCompanyList[currentLine[0]] += 1
                        break
                    #breaks out of nested loop for faster speed?
                    flag = True
                    i += 1
        #if statement for when there are no companies found in companynames.txt
        if companyFound != True:
            print("Company not found \n")
            #creates a file only if a company is not found (to later add it or a variant to the list of companies)
            #joins the paths of tempPath and imageName to update dynamically
            fullTempPath = os.path.join(tempPath, 'time_'+ imageName + str(c) + ".txt")
            #opens the temp path for writing the ocr to a txt file
            file1 = open(fullTempPath, "w")
            file1.write(imageText)
            file1.close() 
            #append path with .png
            copiedPath = inputPath + str(c) + ".png"
            #renames the file path so it can be copied correctly
            os.rename(inputPath, copiedPath)
            #copies the relevent image of the not found company to the text folder (to help debug the not found company)
            shutil.copy(copiedPath, tempPath)
            c += 1

    #deletes the images in the dump folder to avoid extra old results (skips first item because theres a weird permission error with cap.png, and skipping won't affect anything because it always gets overwritten)
    for file in os.scandir(directorydump):
        if not (file.name == 'cap.png'):
            os.remove(file.path)
    #d is the total amount of times this program runs        
    d += 1
    print("total queries: " + str(d))



#prints the final dict list of all found companies 
print(totalCompanyList)

# Get the Keys and store them in a list
labels = list(totalCompanyList.keys())

# Get the Values and store them in a list
values = list(totalCompanyList.values())

#makes pie chart display absolute values instead of percentages
valsum = sum(totalCompanyList.values())
def absolute_value(val):
    a  = numpy.round(val/100.*valsum, 0)
    return a

#displays the contents of totalcompanylist as a pie chart https://stackoverflow.com/questions/41088236/how-to-have-actual-values-in-matplotlib-pie-chart-displayed
plt.pie(values, labels=labels, autopct=absolute_value)
plt.axis('equal')
plt.savefig('D:\\Users\\shrike\\Documents\\python\\main\\chart\\piechart.png')

#plays a sound when the program completes. Helpful for me. 
#winsound.PlaySound('tada.wav', winsound.SND_FILENAME)



# plt.pie(values, labels=labels,
#          autopct=lambda p: '{:.0f}%'.format(p * sum(values) / 100),
#          shadow=True, startangle=90)

# plt.pie(values, labels=labels)
# plt.show()
#
# 
# EVERYTHING BELOW THIS POINT IS LEFT OVER CODE
# 
#    
   
   
   
   
   
    # for line in lines:
    #     print(line)
    #     if line in imageText.lower():
    #         print("Company found: " + line + "\n")
    #     if not line:
    #         break




    # while lineSearch != '':
    #     if(imageText == ''):
    #         print("Empty txt \n")
    #         break
    #     elif(lineSearch in imageText.lower()): 
    #         print ("Company found: " + lineSearch + '\n')
    #         break
        # elif lineSearch == '':
        #     print("Company not found \n")
        #     break
        # else: 
        #     print("force break \n")
        #     break


    #for csv file of company list. legacy because couldn't get it worked. switched to txt file
    # with open("D:\\Users\\shrike\\Documents\\python\\main\\CompanyNames.csv", newline='') as csvfile:
    #     companyFinder = InsensitiveDictReader(csvfile)
    #     for row in companyFinder:
    #         print(str(row))
    #         if(imageText == ''):
    #             print("Empty txt \n")
    #             break
    #         elif(str(row) in imageText):
    #             print("Company found \n")
    #             break
    #         if(row == ''):
    #             break



    #check csv file of companies for matching company https://www.codegrepper.com/code-examples/python/how+to+check+if+a+specific+text+exists+on+txt+file+in+python
    # CompanySearch = open("D:\\Users\\shrike\\Documents\\python\\main\\CompanyNames.csv", 'r')
    # while True:
    #     companyLine = CompanySearch.readline().lower()
    #     print(companyLine)
    #     if(imageText == ''):
    #         print("Empty txt \n")
    #         break
    # # elif(word_in_file(CompanySearch, imageText)):
    # #     print("Company found \n")
    #     elif(CompanySearch.readline().lower() in imageText): 
    #         print ("Company found: " + CompanySearch.readline().lower() + '\n')
    #         break
    #     if CompanySearch.readline().lower() == '':
    #         break
    #     #print("Company not found \n")

    # CompanySearch.close()




# for file in os.listdir(directorydump):
#     img = Image.open(file)
#     why = pytesseract.image_to_string(img)
#     print(why)
    #print(pytesseract.image_to_string(Image.open('dump\' + file)))



# FOR SCROLLING PAGE POTENTIALLY. HARD TO GET WORKING. 

#    if is_element_visible_in_viewpoint != True:
    #    driver.execute_script("window.scrollTo(0, 1080)") 
    # def is_element_visible_in_viewpoint(driver, element) -> bool:
    # return driver.execute_script("var elem = arguments[0],                 " 
    #                              "  box = elem.getBoundingClientRect(),    " 
    #                              "  cx = box.left + box.width / 2,         " 
    #                              "  cy = box.top + box.height / 2,         " 
    #                              "  e = document.elementFromPoint(cx, cy); " 
    #                              "for (; e; e = e.parentElement) {         " 
    #                              "  if (e === elem)                        " 
    #                              "    return true;                         " 
    #                              "}                                        " 
    #                              "return false;                            "
    #                              , element)
