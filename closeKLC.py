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

def closeKLC():
    print("stop LUT")
    print("*** start to end ***")
    try:
        newhdl=0  # I found if the device is on, the handle will be 0, to avoid reinitial KLC, I directly set newhdl as 0
                  # !!!! So when we change KLC we should pay attention on handle number.
        #print(newhdl)
        
        klcClose(newhdl)          
    except Exception as ex:
        print("Warning:", ex)
    print("*** End ***")
    