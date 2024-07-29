# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 11:28:11 2024

@author: Laboratorio
"""


import initialKLCfor1
import closeKLCfor1
import numpy as np
from KLCCommandLib import *
from openpyxl import Workbook
import time
# import asyncio
# import nest_asyncio
# nest_asyncio.apply()


# initial KLC 
# here we also use a=1 to call KLC initial function
# If we need to restart KLC, we should restart the kernal (in the python console)
# To check the handle value of KLC, which is necessary for the following KLC functions.
handle=initialKLCfor1.initialKLC(1)
print("KLC´s handle:",handle)
# seriesName=input("input a name for the new series of captures:")
# =============================================================================
# 
# =============================================================================
vols2=[2,3,4]
# x=np.arange(0,0.8,0.1)
# y=np.arange(0.8,2.1,0.01)
# z=np.arange(2.1,5.1,0.1)
# vols2=np.arange(0,2,0.5)
# config value will be vavriable for judging the type of configuration.
f=1000  # !!!!! set the frequency to the enabled channel
mode=2 # 1 continuous; 2 cycle.
cyclenumber=1 #number of cycles 1~ 2147483648.s
delay=1000  # !!! the sample intervals[ms] 1~ 2147483648
precycle_rest=0 # the delay time before the cycle start[ms] 0~ 2147483648.
hdl=handle
count=0
klcRemoveLastOutputLUT(hdl, count)
def sendVoltage(vols):
   
   l=len(vols)
   volarr =  (c_float * len(vols))(*vols)
   
   if(klcSetOutputLUT(hdl, volarr, l)<0):
       print("klcSetOutputLUT failed")
   klcSetFrequency1(hdl, f)   
   if(klcSetOutputLUTParams(hdl, mode, cyclenumber, delay, precycle_rest)<0):
       print("klcSetOutputLUTParams failed")
   
   print("----------------Current output voltage is:",vols)
   
   

   if(klcStartLUTOutput(hdl)<0):
       print("klcStartLUTOutput failed")
   # command=input("Please press any key to close the current setup: ")
   time.sleep(1)
   

      
   
def main():  
         
    length=len(vols2) #!!!!
    count=1
    while(count<length+1):  
        vols1=[vols2[count-1]]   
         
        sendVoltage(vols1)
        # with asyncio.Runner() as runner:
        #     runner.run(sendVoltage(vols1))
        count+=1

if __name__=="__main__":
    main()



# =============================================================================
#                    close all the devices
# =============================================================================
# input y will close all device, any other input will keep pd work, but KLC will be closed anyway
print("The measurement is done.")
closeKLCfor1.closeKLC(handle)