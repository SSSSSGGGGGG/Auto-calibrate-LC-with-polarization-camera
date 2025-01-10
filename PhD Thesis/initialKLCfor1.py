# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 11:28:23 2024

@author: Laboratorio
"""

try:
    from KLCCommandLib import *
except OSError as ex:
    print("Warning:",ex)

def initialKLC(a):
    print("*** Initial KLC ***")
    if a:
        try:
            devs = klcListDevices()  # device number of KLC
            print(devs)
            if(len(devs)<=0):
               print('There is no devices connected')
               exit()
            sn1 = devs[0][0]
            print("connect ",sn1)
            hdl1 = klcOpen(sn1, 115200, 3)    
           
            if(hdl1<0):
                print("open ", sn1, " failed")
                exit()
            if(klcIsOpen(sn1) == 0):
                print("klcIsOpen failed")
                klcClose(hdl1)
                exit()
            
            
        except Exception as ex:
            print("Warning:", ex)
    
    return hdl1