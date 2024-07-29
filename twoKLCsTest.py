# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 11:28:11 2024

@author: SG
"""
import time
import initialKLC
import closeKLC
import numpy as np
from KLCCommandLib import *

handle1,handle2=initialKLC.initialKLC(1)
print("KLC´s handle:",handle1,handle2)

vol1=[1.4,2.2,1.65,1.65,1.65,1.65]
vol2=[1.4,1.4,1.65,1.5,1.4,1.4]
# config value will be vavriable for judging the type of configuration.
f=1000  # !!!!! set the frequency to the enabled channel
mode=2 # 1 continuous; 2 cycle.
cyclenumber=1 #number of cycles 1~ 2147483648.s
delay=1000  # !!! the sample intervals[ms] 1~ 2147483648
precycle_rest=0  # the delay time before the cycle start[ms] 0~ 2147483648.
 
def sendVoltage(v1,v2):
    l1=len(v1)
    volarr1 =  (c_float * len(v1))(*v1)
    l2=len(v2)
    volarr2 =  (c_float * len(v2))(*v2)
    if(klcSetOutputLUT(handle1, volarr1, l1)<0):
        print("klc1SetOutputLUT failed")
    if(klcSetOutputLUT(handle2, volarr2, l2)<0):
        print("klc2SetOutputLUT failed")    
    if(klcSetOutputLUTParams(handle1, mode, cyclenumber, delay, precycle_rest)<0):
        print("klc1SetOutputLUTParams failed")                
    if(klcSetOutputLUTParams(handle2, mode, cyclenumber, delay, precycle_rest)<0):
        print("klc2SetOutputLUTParams failed")
    
    print("-----LC1-Current output voltage is:",v1,"---LC2-Current output voltage is:",v2) 
          
    if(klcStartLUTOutput(handle1)<0):
        print("klc1StartLUTOutput failed")
    if(klcStartLUTOutput(handle2)<0):
        print("klc2StartLUTOutput failed")
    time.sleep(1)



def main():      
    length1=len(vol1)
    count=1
    while(count<length1+1):  
        vols1=[vol1[count-1]] 
        vols2=[vol2[count-1]]
        print(f"vols1 ={vols1},vols2 ={vols2}")
        sendVoltage(vols1, vols2)
        count+=1
    # time.sleep(2) 

if __name__=="__main__":
    main()
    
print("The measurement is done.")
closeKLC.closeKLC(handle1,handle2)