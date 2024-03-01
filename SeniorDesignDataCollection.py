# March 2
# 
# run by: python Arduino60on60off.py <saveas_file_name> 

# psuedocode:
# calibrate temperature range from 15 (min) to 40 (max)
# control relay to turn arduino on for 60 seconds
# let arduino run for 
# control relay to turn arduino off for 60 seconds

from cmath import e
import sys
import os
from os import path
import subprocess
# import pyvisa
import time
import numpy as np
import pyautogui as pg
from relaycontrol import relaycontrol

#while(1):
#    print(pg.position())
    
def open_flir():
    app_path = r"C:\Program Files\FLIR Systems\FLIR Research Studio\FLIR Research Studio.exe"
    try:
        proc = subprocess.Popen([app_path])
        time.sleep(5)
        pg.hotkey('win','up')
        time.sleep(8)
        return proc
    except FileNotFoundError:
        print('Error: file not found')
    except Exception as e:
        print(e)


# def setVoltage(value):
#     commandStr = "CH1:Voltage " + str(value)
#     print(commandStr)
#     spd.write(commandStr)
#     time.sleep(0.5)


# def connectDevices():
#     _rm = pyvisa.ResourceManager()
#     sds = -1
#     spd = -1
#     my = -1
#     for i in _rm.list_resources():
#         if(i.find('SDS') >= 0):
#             sds = _rm.open_resource(i)
#         if(i.find('SPD') >= 0):
#             spd = _rm.open_resource(i)
#         if(i.find('MY') >= 0):
#             my = _rm.open_resource(i)
#     return (sds, spd, my)

##############################################################################

#### Device Setup ####
# (sds, spd, my) = connectDevices()

# if(spd != -1):
#     print('spd connected')
# else:
#     print('spd not connected')
        
if len(sys.argv) < 3:
    print(f"Error: no filename specified. Usage: {sys.argv[0]} file_name iterations", file=sys.stderr)
    sys.exit(1)

iterations = int(sys.argv[2])

relaycontrol.init()

for i in range(iterations):

    ##### Open FLIR app #####
    flir = open_flir()

    ##### Open camera #####
    pg.click(x=1824, y=39)  # Dismiss the red banner at the top
    time.sleep(2)
    pg.click(x=186, y=66)  # Scan for cameras
    time.sleep(5)
    pg.click(x=412, y=173)  # Connect button
    time.sleep(10)
    pg.click(x=953, y=523)  # "Place in this frame"

    ##### Turn On Power Supply #####
    relaycontrol.off()
    time.sleep(2)
    print("START!")
    time.sleep(3)
    pg.hotkey("F5") #record button
    time.sleep(1)

    ##### Start #####
    #setVoltage(10)
    relaycontrol.on()


    time.sleep(60 * 4)


    #### Close Test ###
    relaycontrol.off()

    time.sleep(60 * 4)


    print("DONE!!")
    pg.hotkey('ctrl', 'F5') #record button


    fileName = sys.argv[1]
    # "addedComponent_B_3_3.seq";
    print(fileName)

    while True:
        try:       
            print('trying')
            #move and rename
            with os.scandir("C:\\Users\\MHStudent\\Documents\\Research Studio Data\\") as fileList:
                sortedList = sorted(fileList, key=lambda entry:entry.stat().st_birthtime, reverse=True)
                scr = sortedList[0].path
            dst = f'.\\RecordedVideos\\{fileName}_{i}.seq'
            print(scr)
            print(dst)
            os.rename(scr,dst)
            break
        except:    
            print('Failed to move, retrying')
            time.sleep(0.5)
            pass

    flir.terminate()

relaycontrol.close()

