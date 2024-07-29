# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 14:30:08 2024

@author: Laboratorio
"""

try:
    from KLCCommandLib import *
    import time
    import initialKLC
except OSError as ex:
    print("Warning:",ex)

def closeKLC(handle1,handle2,handle3):
    print("stop LUT")
    print("*** start to end ***")
    try:
        hdl1=handle1  # I found if the device is on, the handle will be 0, to avoid reinitial KLC, I directly set newhdl as 0
        hdl2=handle2          # !!!! So when we change KLC we should pay attention on handle number.
        hdl3=handle3
        #print(newhdl)
        klcStopLUTOutput(hdl1)
        klcStopLUTOutput(hdl2)
        klcStopLUTOutput(hdl3)        
        klcClose(hdl1)
        klcClose(hdl2)  
        klcClose(hdl3)        
    except Exception as ex:
        print("Warning:", ex)
    print("*** End ***")
    