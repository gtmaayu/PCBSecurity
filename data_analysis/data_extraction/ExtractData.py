import os
import time
import pyautogui as pg  # mouse position library
import cv2
import numpy as np
from .. import find_main_chip

pg.FAILSAFE = False

rootPath = "C:\\Users\\MHStudent\\Desktop\\Senior Design\\RecordedVideos"
os.chdir(rootPath)


def findAnchor(rawPath, destPath):
    # Read image.
    img = cv2.imread(rawPath, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return find_main_chip.find_center_chip(gray)[0]





def save_file(name, ext):
    time.sleep(7)
    pg.click(x=1899, y=321)  # export opt
    pg.click(x=1774, y=322)  # csv button
    time.sleep(5)
    name = name[0:len(name)-4]
    fileName = name + ext
    time.sleep(3)
    pg.write(fileName)
    time.sleep(3)
    pg.press('tab')  # press the Enter key
    pg.press('tab')  # press the Enter key
    pg.press('tab')  # press the Enter key
    pg.press('tab')  # press the Enter key
    pg.press('tab')  # press the Enter key
    pg.press('tab')  # press the Enter key
    time.sleep(3)
    pg.press('enter')  # press the Enter key
    time.sleep(3)
    pg.write("C:\\Users\\MHStudent\\Desktop\\Senior Design\\ExtractedData")
    time.sleep(3)
    pg.press('enter')  # press the Enter key
    time.sleep(1)
    pg.click(x=790, y=530)  # save button
    time.sleep(3)


#dirs = os.listdir()
#dirs = ["addedComponent","baseline","longerTrace","removedComponent","thickerTrace"]
dirs = ["C:\\Users\\MHStudent\\Desktop\\Senior Design\\RecordedVideos"]
print(dirs)


def click(x, y):
    pg.moveTo(x, y)
    time.sleep(1)
    pg.click(x, y)

def offset(anchor_coord):
    atmega_coord_left = [973,504] 
    return [atmega_coord_left[0] - anchor_coord[0],atmega_coord_left[1] - anchor_coord[1]]

def generatePlot(x, y):
    click(x=407, y=904)  # stat button
    click(x=413, y=864)  # temporal
    click(x, y)  # oval
    click(x+218, y-9)  # oval
    click(x=1212, y=543)  # side


for i1 in range(len(dirs)):
    os.chdir(dirs[i1])
    files = os.listdir()
    print(files)

    for i2 in range(len(files)):
        # if(files[i2] == "regions_detected" or files[i2] == "anchor" or files[i2] == "raw"):
        #     continue

        # start
        run = "start /max " + rootPath + "\\" + dirs[i1] + "\\" + files[i2]
        print(run)
        os.system(run)

        time.sleep(10)
        #todo go to the scroll bar and go to 1 min


        pg.hotkey(" ")
        # click(x=261, y=956)
        # click(x=261, y=956)
        # click(x=261, y=956)
        # click(x=261, y=956)

        # pg.moveTo(1691, 789)
        # pg.dragTo(1697, 523, 1, button='left')
        # time.sleep(1)
        # click(x=1663, y=647)

        # save screenshot
        picname = dirs[i1] + "_" + \
            (files[i2])[0:len(files[i2])-4] + "_raw_screenshot.png"
        rawPath = rootPath + "\\" + dirs[i1] + "\\raw\\" + picname
        pg.screenshot(rawPath, region=(507, 145, 1394-507, 809-145))
        print("screenshot saved to ", rawPath)

        # find the anchor
        picname = dirs[i1] + "_" + \
            (files[i2])[0:len(files[i2])-4] + "_anchor_screenshot.png"
        destPath = rootPath + "\\" + dirs[i1] + "\\anchor\\" + picname
        anchorPos = findAnchor(rawPath, destPath)

        anchorPos[0] = -(973) + 503 + anchorPos[0]
        anchorPos[1] = -(504) + 146 + anchorPos[1]

        speedDur = 0.3

        click(492, 43)  # rect1 samd
        pg.moveTo(anchorPos[0] + 900, anchorPos[1] + 485)
        pg.dragTo(anchorPos[0] + 934, anchorPos[1] +
                  518, speedDur, button='left')

        # click(492, 43)  # rect2
        # pg.moveTo(anchorPos[0] + 447, anchorPos[1] + 245)
        # pg.dragTo(anchorPos[0] + 479, anchorPos[1] +
        #           302, speedDur, button='left')

        # click(492, 43)  # rect3
        # pg.moveTo(anchorPos[0] + 392, anchorPos[1] + 167)
        # pg.dragTo(anchorPos[0] + 451, anchorPos[1] +
        #           220, speedDur, button='left')

        # click(492, 43)  # rect4
        # pg.moveTo(anchorPos[0] + 366, anchorPos[1] + 271)
        # pg.dragTo(anchorPos[0] + 422, anchorPos[1] +
        #           317, speedDur, button='left')

        # click(492, 43)  # rect5
        # pg.moveTo(anchorPos[0] + 646, anchorPos[1] + 325)
        # pg.dragTo(anchorPos[0] + 679, anchorPos[1] +
        #           382, speedDur, button='left')

        # add component like this
        # click(492, 43) #rect5
        #pg.moveTo(anchorPos[0] + 646, anchorPos[1] + 325)
        #pg.dragTo(anchorPos[0] + 679, anchorPos[1] + 382, speedDur, button='left')

        time.sleep(1)

        # save screenshot
        picname = dirs[i1] + "_" + (files[i2])[0:len(files[i2])-4] + \
            "_regions_detected_screenshot.png"
        shortPath = rootPath + "\\" + dirs[i1] + "\\regions_detected"
        fullpath = shortPath + "\\" + picname
        pg.screenshot(fullpath, region=(503, 146, 1400-503, 811-146))
        print("screenshot saved to ", fullpath)

        time.sleep(1)
        click(1766, 907)  # profile button
        click(1750, 860)  # profile button
        # click(1766+218, 907-9)#oval

        click(x=1519, y=667)  # circ 1
        click(x=1519+218, y=667-9)  # circ 1

        # click(1738,633)#maximum

        click(x=1169, y=549)  # place right

        save_file(files[i2], "_inductor")

        generatePlot(x=165, y=712)
        save_file(files[i2], "_clock")

        generatePlot(x=170, y=759)
        save_file(files[i2], "_diode")

        generatePlot(x=173, y=803)
        save_file(files[i2], "_res")

        generatePlot(x=175, y=850)
        save_file(files[i2], "_trans")

        generatePlot(x=177, y=879)
        save_file(files[i2], "_trace")

        # extra plot
        #generatePlot(x=177, y=879)
        # save_file(files[i2],"_trace")

        # kill
        kill = "taskkill /F /IM \"FLIR Research Studio.exe\" /T"
        os.system(kill)

    os.chdir("..")
