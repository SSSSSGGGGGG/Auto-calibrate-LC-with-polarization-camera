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

try:
    devs = klcListDevices()  # device number of KLC
    print(devs)
    if(len(devs)<=0):
       print('There is no devices connected')
       exit()
    sn1 = devs[0][0]
    
    # sn1=devs[0][0]
    print("connect ",sn1)
    print("if there is a device opening",klcIsOpen(sn1))
    hdl1 = klcOpen(sn1, 115200, 3)    
    
    if(hdl1<0):
        print("open ", sn1, " failed")
        exit()
    if(klcIsOpen(sn1) == 0):
        print("klcIsOpen failed")
        klcClose(hdl1)
        exit()
    klcSetEnable(hdl1, 2)
    print("stop LUT")
    print("*** start to end ***")
    # klcStopLUTOutput(hdl1)
    
    klcClose(hdl1)
    print("*** End ***")
except Exception as ex:
    print("Warning:", ex)
    

    