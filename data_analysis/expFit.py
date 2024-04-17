#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exponential fitting
using scipy.optimize.curve_fit

Created on Wed Oct 27 16:23:35 2021
Modified for Nano Every boards and mic hack Apr 17 2024

@author: Jacky (original), Elliot (Nano Every modofications)
"""
import os
import numpy as np
import pandas as pd
import glob
import itertools
import csv
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def func(t,a,b,c):
    return -a * np.exp(-b*t) + c

def fit(data,col,filename, *, up):
    ydata = list(data[col])
    # get the pivot point
    #imax = ydata.index(max(ydata))
    imax=len(ydata) // 2
    if up:
        ydata = np.asarray(ydata[0:imax])
        t_data = np.asarray(list(data['reltime'])[0:imax])
    else:
        ydata = np.asarray(ydata[imax:])
        t_data = np.asarray(list(data['reltime'])[imax:])

    t_data = t_data-t_data[0] #shift the t so it start from 0
    
    para,db = curve_fit(func,t_data,ydata,maxfev=1000)
    plt.figure()
    plt.plot(t_data,ydata)
    plt.plot(t_data,func(t_data,*para),label='fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(para))
    plt.legend()
    direction = "up" if up else "down"
    plt.savefig("../fittingDataPlots/"+filename+"_"+direction+".pdf")
    # plt.show()
    return para[0],para[1],para[2]
   

path = '../RecordedVideos/flir_csv' # CHANGE TO YOUR OWN PATH
typeList = itertools.product(["baseline", "microphone"], ["A", "B", "C", "D", "E"], range(5))
# Order below must match order in exported FLIR CSVs
compList = ['samd','atmega','3v3reg','buck','usbesd','fullboard']
li = []

with open("../RecordedVideos/fittingParameters.csv", "w") as csvFile:
    fieldnames = ['Board Type','Board Instance','Component','Trial','a_rise','b_rise','c_rise', 'a_fall', 'b_fall', 'c_fall']
    writer = csv.DictWriter(csvFile, fieldnames=fieldnames)
    writer.writeheader()

    for bType, instance, trial in typeList:
        # Ex "april10_baselineBoardA_0"
        t = f"*_{bType}Board{instance}_{trial}.csv"
        currentPath = path+os.path.sep+t
        print(t)
        all_files = glob.glob(currentPath)
        if len(all_files) != 1:
            print(f"Got {len(all_files)} files for {t} - expected 1")
            if not all_files:
                continue
        final_path = all_files[0]
        df = pd.read_csv(final_path, index_col=None, header=0)
        # Rename columns to match components
        df.columns = ['frame','abstime','reltime'] + compList
        for c in compList:                                   
            #subtraction
            tempData = list(df[c])
            initAvg = sum(tempData[0:5])/len(tempData[0:5])
            df[c]=df[c]-initAvg
            plotName = f"{bType}Board{instance}_{trial}_{c}"
                    
            try:
                ar, br, cr = fit(df, c, plotName, up=True)
            except:
                ar="N/A"
                br="N/A"
                cr="N/A"
            pass
                    
            try:
                af, bf, cf = fit(df, c, plotName, up=False)
            except:
                af="N/A"
                bf="N/A"
                cf="N/A"
            pass
            li.append(df)
            writer.writerow({'Board Type':bType,'Board Instance':instance,'Component':c,'Trial':trial\
                                        ,'a_rise':ar,'b_rise':br,'c_rise':cr, 'a_fall':af, 'b_fall':bf, 'c_fall':cf})
            
