# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 14:38:56 2024

@author: Laboratorio

"""
import initialKLC
import closeKLC
import sendVoltages2
import numpy as np
import measurePower2 as mp
from KLCCommandLib import *
import time
import asyncio
import nest_asyncio
nest_asyncio.apply()
# It can only be started one time
a=1
b=initialKLC.initialKLC(a)
print(b)
hdl=0
f=1000  # set the frequency to the enabled channel
mode=2 # 1 continuous; 2 cycle.
cyclenumber=1 #number of cycles 1~ 2147483648.
delay=2000  #the sample intervals[ms] 1~ 2147483648
precycle_rest=0  # the delay time before the cycle start[ms] 0~ 2147483648.
sendVoltages2.setChannelandParameters(f)
# vols=np.arange(0.8,1.1,0.1)
vols=[1]
length=len(vols)
#sendVoltages2.sendVoltage(vols,cyclenumber, mode, delay, precycle_rest,length)
volarr =  (c_float * len(vols))(*vols)
print("set LUT array")
async def KLC():
    if(klcSetOutputLUT(0, volarr, length)<0):
        print("klcSetOutputLUT failed")
    print("set LUT parameters")
    if(klcSetOutputLUTParams(hdl, 2, 3, 1000, 0)<0):
        print("klcSetOutputLUTParams failed")
    task=asyncio.create_task(photodiode())
    if(klcStartLUTOutput(hdl)<0):
        print("klcStartLUTOutput failed")
    
    await task
    #await asyncio.sleep(1)
    active=[None]
    f=[None]
    err=[None]
    ch=[None]
    v=[None]
    t=0
    while(t<length):
        klcGetOutPutStatus(hdl, active, v, f, err)
        print("Get LUT output: ", active ," voltage: ",  v ," frequency: " , f, " errFlag ", err)
        time.sleep(1)
        t+=1
     
   
async def photodiode():
    sleep=1  # !!!! it couldnot be very small, we should check it in practice, unit is "s"
    mp.measureAction(sleep,"c",5,"filename")
    await asyncio.sleep(1)
    
asyncio.run(KLC())

closeKLC.closeKLC()
