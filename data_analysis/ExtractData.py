import os
import time
import pyautogui as pg  # mouse position library
import cv2
import sys
import numpy as np

import find_main_chip

pg.FAILSAFE = False

rootPath = "C:\\Users\\MHStudent\\Desktop\\Senior_Design"
os.chdir(rootPath)


def findAnchor(rawPath):
    # Read image.
    img = cv2.imread(rawPath, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    x = find_main_chip.find_atmega_right_corner(gray)


    a, b, r = x[0], x[1], 2

    # Draw the circumference of the circle.
    cv2.circle(img, (a, b), r, (0, 255, 0), 2)
    print("x: ",a)
    print("y: ",b)
    # Draw a small circle (of radius 1) to show the center.
    img1 = cv2.circle(img, (a, b), 1, (0, 0, 255), 3)
    cv2.imshow("Detected Circle", img)
    cv2.imwrite(rawPath, img)
    cv2.imwrite(rawPath+"_marked", img1)
    

    #cv2.waitKey(0)
    return [a, b]





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
    pg.write("C:\\Users\\MHStudent\\Desktop\\Senior_Design\\ExtractedData")
    time.sleep(3)
    pg.press('enter')  # press the Enter key
    time.sleep(1)
    pg.click(x=790, y=530)  # save button
    time.sleep(3)

dirs = ["RecordedVideos"]
print("dirs are")
print(dirs)


def click(x, y):
    pg.moveTo(x, y)
    time.sleep(1.5)
    pg.click(x, y)


for i1 in range(len(dirs)):

    os.chdir(dirs[i1])
    files = os.listdir()
    #skip zips
    completed_files = [file[:-4] + ".seq" for file in os.listdir("C:\\Users\\MHStudent\\Desktop\\Senior_Design\\RecordedVideos\\flir_csv\\")]
    files = [file for file in files if file.endswith('.seq') and file not in completed_files]
    print(files)

    for i2 in range(len(files)):
        # if(files[i2] == "regions_detected" or files[i2] == "anchor" or files[i2] == "raw"):
        #     continue

        # start
        try:
            run = "start /max " + rootPath + "\\" + dirs[i1] + "\\" + files[i2]
            print(run)
            os.system(run)

            time.sleep(10)
            # go to the scroll bar and go to 1 minPoint(x=530, y=826)(heating), Point(x=1138, y=831)(cooling)
            click(530,826)
            time.sleep(2)


            #pg.hotkey(" ")
            click(x=976, y=895)
            time.sleep(2)

            # save screenshot
            picname = dirs[i1] + "_" + \
                (files[i2])[0:len(files[i2])-4] + "_raw_screenshot.png"
            rawPath = rootPath + "\\" + dirs[i1] + "\\raw\\" + picname
            pg.screenshot(rawPath, region=(507, 145, 1394-507, 809-145))
            print("screenshot saved to ", rawPath)

            # find the anchor
            picname = dirs[i1] + "_" + \
                (files[i2])[0:len(files[i2])-4] + "_anchor_screenshot.png"
            #destPath = rootPath + "\\" + dirs[i1] + "\\anchor\\" + picname
            anchorP = findAnchor(rawPath)
            anchorPos =[0,0]
            offset_x = 0 #only if needed for adjustment
            left_corner =[973,504]
            right_corner =[1054,503]

            anchorPos[0] = -(right_corner[0]-offset_x) + 503 + anchorP[0]
            anchorPos[1] = -(right_corner[1]) + 146 + anchorP[1]

            
            click(492, 43)  
            pg.moveTo(anchorPos[0] , anchorPos[1] )

            speedDur = 0.3

            click(492, 43)  # rect1 samd
            pg.moveTo(anchorPos[0] + 900, anchorPos[1] + 485)
            pg.dragTo(anchorPos[0] + 934, anchorPos[1] +
                    518, speedDur, button='left')
            

            # polygon1 atmega
            
            click(x=528, y=53)

            click(x=503, y=180)
            pg.moveTo(anchorPos[0] + 1013, anchorPos[1] + 464)
            pg.dragTo(anchorPos[0] + 1054, anchorPos[1] +
                    503, speedDur, button='left')
            pg.dragTo(anchorPos[0] + 1014, anchorPos[1] +
                546, speedDur, button='left')
            pg.dragTo(anchorPos[0] + 973, anchorPos[1] +
                504, speedDur, button='left')
            
            click(x=528, y=53) 
            click(x=498, y=84)

            # rect2 3.3 regulator
            click(492, 43)  
            pg.moveTo(anchorPos[0] + 904, anchorPos[1] + 527)
            pg.dragTo(anchorPos[0] + 916, anchorPos[1] +
                    552, speedDur, button='left')

            click(492, 43)  # rect3 mpm3610 buck conv
            pg.moveTo(anchorPos[0] + 862, anchorPos[1] + 516)
            pg.dragTo(anchorPos[0] + 889, anchorPos[1] +
                    558, speedDur, button='left')

            click(492, 43)  # rect4 USB voltage diode
            pg.moveTo(anchorPos[0] + 796, anchorPos[1] + 462)
            pg.dragTo(anchorPos[0] + 818, anchorPos[1] +
                    476, speedDur, button='left')

            click(492, 43)  # rect5 full board
            pg.moveTo(anchorPos[0] + 741, anchorPos[1] + 450)
            pg.dragTo(anchorPos[0] + 1110, anchorPos[1] +
                    557, speedDur, button='left')
            time.sleep(1)

            # save screenshot
            picname = dirs[i1] + "_" + (files[i2])[0:len(files[i2])-4] + \
                "_regions_detected_screenshot.png"
            shortPath = rootPath + "\\" + dirs[i1] + "\\regions_detected"
            fullpath = shortPath + "\\" + picname
            pg.screenshot(fullpath, region=(503, 146, 1400-503, 811-146))
            print("screenshot saved to ", fullpath)

            time.sleep(1)
            SPLIT_PLOT_BASED_MODULE = (407, 896)
            SPLIT_TEMPORAL_PLOT_BASED_MODULE = (443, 853)
            MERGE_INTO_MODULE =(1311,542)

            #save plots
            #plot based
            click(x=1768,y=892)
            #temp plot module
            click(x=1720, y=851)
            #rect 1
            click(x=1500,y=659)
            #max
            click(x=1659,y=662)
            #place right
            click(x=1131,y=554)
            #plot based
            click(*SPLIT_PLOT_BASED_MODULE)
            #temp plot
            click(*SPLIT_TEMPORAL_PLOT_BASED_MODULE)
            #ploygon1
            click(x=188,y=709)
            #max
            click(x=417,y=702)
            #merge into curr module
            click(*MERGE_INTO_MODULE)
            #plot based
            click(*SPLIT_PLOT_BASED_MODULE)
            #temp plot
            click(*SPLIT_TEMPORAL_PLOT_BASED_MODULE)


            #rect2
            click(x=193,y=751)
            #max
            click(x=347,y=740)
            click(*MERGE_INTO_MODULE)
            #plot based
            click(*SPLIT_PLOT_BASED_MODULE)
            #temp plot
            click(*SPLIT_TEMPORAL_PLOT_BASED_MODULE)

            #rect 3
            click(x=212,y=802) 
            #max
            click(x=351, y=785)

            click(*MERGE_INTO_MODULE)
            #plot based
            click(*SPLIT_PLOT_BASED_MODULE)
            #temp plot
            click(*SPLIT_TEMPORAL_PLOT_BASED_MODULE)

            #rect 4

            click(x=142,y=835) 
            #max
            click(x=392,y=838)

            click(*MERGE_INTO_MODULE)
            #plot based
            click(*SPLIT_PLOT_BASED_MODULE)
            #temp plot
            click(*SPLIT_TEMPORAL_PLOT_BASED_MODULE)
            # time.sleep(2)
            # pg.scroll(5,x=268,y=546)
            # time.sleep(2)

            #rect5
            click(224, y=875) 
            #avg
            click(x=437, y=921)

            click(*MERGE_INTO_MODULE)

            #rescale image
            click(x=607,y=900)
            click(x=1857,y=897)

            time.sleep(10)

            #export options
            click(x=1894,y=326)

            #export measurements to csv
            click(x=1706,y=323)

            time.sleep(2)

            #type file name hit enter
            print(files[i2][:-4])
            pg.write(files[i2][:-4])
            time.sleep(2)
            

            #enter to save file (assumimg file is saved in documents)
            pg.hotkey("enter")
            time.sleep(5)

            scr ="C:\\Users\\MHStudent\\Documents\\" + files[i2][:-4] +".csv" 
            dst = "C:\\Users\\MHStudent\\Desktop\\Senior_Design\\RecordedVideos\\flir_csv\\" + files[i2][:-4] +".csv"

            os.rename(scr,dst)

            time.sleep(15)
            
            #export options
            click(x=1894,y=326)


            click(x=1750,y=375)#export png

            time.sleep(2)

            #type file name hit enter
            pg.write(files[i2][:-4]+".png")
            time.sleep(2)
            pg.hotkey("enter")
            time.sleep(2)
            scr ="C:\\Users\\MHStudent\\Documents\\" + files[i2][:-4]+ ".png"
            dst = "C:\\Users\\MHStudent\\Desktop\\Senior_Design\\RecordedVideos\\flir_png\\" + files[i2][:-4] +".png"

            os.rename(scr,dst)


            # kill
            kill = "taskkill /F /IM \"FLIR Research Studio.exe\" /T"
            os.system(kill)
        except Exception as e:
            print(e)
    os.chdir("..")
